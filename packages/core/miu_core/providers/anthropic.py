"""Anthropic Claude provider."""

from collections.abc import AsyncIterator
from typing import Any

from miu_core.models import (
    Message,
    MessageStopEvent,
    Response,
    StreamEvent,
    TextContent,
    TextDeltaEvent,
    ToolUseContent,
    ToolUseInputEvent,
    ToolUseStartEvent,
)
from miu_core.providers.base import LLMProvider, ToolSchema
from miu_core.providers.converters import build_response, convert_messages_to_anthropic
from miu_core.tracing import Tracer, get_tracer
from miu_core.tracing.types import SpanAttributes

try:
    from anthropic import AsyncAnthropic
except ImportError as e:
    raise ImportError("anthropic package required. Install with: uv add miu-core[anthropic]") from e


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model
        self._client = AsyncAnthropic()
        self._tracer: Tracer = get_tracer("miu.provider")

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Send messages to Claude and get response."""
        with self._tracer.start_as_current_span("provider.complete") as span:
            span.set_attribute(SpanAttributes.PROVIDER_NAME, self.name)
            span.set_attribute(SpanAttributes.PROVIDER_MODEL, self.model)

            api_messages = convert_messages_to_anthropic(messages)

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": max_tokens,
            }
            if system:
                kwargs["system"] = system
            if tools:
                kwargs["tools"] = tools

            response = await self._client.messages.create(**kwargs)
            result = self._convert_response(response)

            # Record token usage and stop reason
            if result.usage:
                span.set_attribute(SpanAttributes.PROVIDER_TOKENS_INPUT, result.usage.input_tokens)
                span.set_attribute(
                    SpanAttributes.PROVIDER_TOKENS_OUTPUT, result.usage.output_tokens
                )
            span.set_attribute(SpanAttributes.PROVIDER_STOP_REASON, result.stop_reason)

            return result

    def _convert_response(self, response: Any) -> Response:
        """Convert Anthropic response to internal format."""
        content: list[TextContent | ToolUseContent] = []

        for block in response.content:
            if block.type == "text":
                content.append(TextContent(text=block.text))
            elif block.type == "tool_use":
                content.append(
                    ToolUseContent(
                        id=block.id,
                        name=block.name,
                        input=block.input,
                    )
                )

        return build_response(
            response_id=response.id,
            content=content,
            stop_reason=response.stop_reason or "end_turn",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Stream messages from Claude."""
        api_messages = convert_messages_to_anthropic(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        # Track tool IDs by their content block index
        tool_ids_by_index: dict[int, str] = {}

        async with self._client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "tool_use":
                        tool_ids_by_index[event.index] = block.id
                        yield ToolUseStartEvent(id=block.id, name=block.name)
                elif event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        yield TextDeltaEvent(text=delta.text)
                    elif delta.type == "input_json_delta":
                        # Use the tracked tool id for this index
                        tool_id = tool_ids_by_index.get(event.index, str(event.index))
                        yield ToolUseInputEvent(
                            id=tool_id,
                            input_delta=delta.partial_json,
                        )
                elif event.type == "message_stop":
                    # Get final message for stop reason and usage
                    final = await stream.get_final_message()
                    usage_dict = None
                    if final.usage:
                        usage_dict = {
                            "input_tokens": final.usage.input_tokens,
                            "output_tokens": final.usage.output_tokens,
                        }
                    yield MessageStopEvent(
                        stop_reason=final.stop_reason or "end_turn",
                        usage=usage_dict,
                    )
