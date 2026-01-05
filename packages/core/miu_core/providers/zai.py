"""ZhipuAI (智谱AI) provider using zai-sdk.

Supports two API endpoints:
- Coding Plan: https://open.bigmodel.cn/api/coding/paas/v4 (default)
- Standard API: https://open.bigmodel.cn/api/paas/v4

Set ZAI_BASE_URL env var to switch endpoints.
"""

import asyncio
import json
import os
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
)
from miu_core.providers.base import LLMProvider, ToolSchema
from miu_core.providers.converters import (
    build_response,
    convert_tools_to_openai,
    map_openai_stop_reason,
)

try:
    from zai import ZhipuAiClient
except ImportError as e:
    raise ImportError("zai-sdk package required. Install with: uv add miu-core[zai]") from e

# API endpoints
ZAI_CODING_URL = "https://open.bigmodel.cn/api/coding/paas/v4"
ZAI_STANDARD_URL = "https://open.bigmodel.cn/api/paas/v4"


class ZaiProvider(LLMProvider):
    """ZhipuAI (智谱AI) LLM provider using zai-sdk.

    Uses ZAI_BASE_URL env var if set, otherwise defaults to coding plan endpoint.
    """

    name = "zai"

    def __init__(self, model: str = "glm-4.7") -> None:
        self.model = model
        # Use ZAI_BASE_URL if set, otherwise default to coding plan
        base_url = os.environ.get("ZAI_BASE_URL", ZAI_CODING_URL)
        self._client = ZhipuAiClient(base_url=base_url)

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Send messages to Z.AI and get response."""
        api_messages = self._convert_messages(messages, system)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = convert_tools_to_openai(tools)

        # Wrap sync client call in thread for async compatibility
        response = await asyncio.to_thread(self._client.chat.completions.create, **kwargs)
        return self._convert_response(response)

    def _convert_messages(
        self, messages: list[Message], system: str | None
    ) -> list[dict[str, Any]]:
        """Convert internal messages to OpenAI-compatible format."""
        result: list[dict[str, Any]] = []

        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            if msg.role == "system":
                result.append({"role": "system", "content": msg.get_text()})
            elif isinstance(msg.content, str):
                result.append({"role": msg.role, "content": msg.content})
            else:
                for block in msg.content:
                    if isinstance(block, TextContent):
                        result.append({"role": msg.role, "content": block.text})
                    elif isinstance(block, ToolUseContent):
                        result.append(
                            {
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "id": block.id,
                                        "type": "function",
                                        "function": {
                                            "name": block.name,
                                            "arguments": str(block.input),
                                        },
                                    }
                                ],
                            }
                        )
                    else:
                        # Tool result
                        result.append(
                            {
                                "role": "tool",
                                "tool_call_id": block.tool_use_id,
                                "content": block.content,
                            }
                        )

        return result

    def _convert_response(self, response: Any) -> Response:
        """Convert Z.AI response to internal format."""
        choice = response.choices[0]
        message = choice.message
        content: list[TextContent | ToolUseContent] = []

        if message.content:
            content.append(TextContent(text=message.content))

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_input: dict[str, Any] = {}
                if tool_call.function.arguments:
                    try:
                        tool_input = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}
                content.append(
                    ToolUseContent(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        input=tool_input,
                    )
                )

        return build_response(
            response_id=response.id if hasattr(response, "id") else "zai-response",
            content=content,
            stop_reason=map_openai_stop_reason(choice.finish_reason),
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Stream messages from Z.AI."""
        api_messages = self._convert_messages(messages, system)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = convert_tools_to_openai(tools)

        # Use queue to pass chunks from sync thread to async context
        queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def process_stream() -> None:
            """Process stream in thread and put events on queue."""
            try:
                stream_response = self._client.chat.completions.create(**kwargs)
                finish_reason = None
                for chunk in stream_response:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        asyncio.run_coroutine_threadsafe(
                            queue.put(TextDeltaEvent(text=delta.content)),
                            loop,
                        )
                    if chunk.choices[0].finish_reason:
                        finish_reason = chunk.choices[0].finish_reason
                # Signal completion
                asyncio.run_coroutine_threadsafe(
                    queue.put(MessageStopEvent(stop_reason=map_openai_stop_reason(finish_reason))),
                    loop,
                )
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        # Start streaming in background thread
        loop.run_in_executor(None, process_stream)

        # Yield events from queue
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event
