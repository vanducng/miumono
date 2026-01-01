"""Shared message and response conversion utilities for LLM providers.

Provides common conversion patterns to reduce duplication across provider implementations.
"""

from typing import Any

from miu_core.models import (
    Response,
    TextContent,
    ToolResultContent,
    ToolUseContent,
    Usage,
)
from miu_core.models.messages import Message


def convert_content_block_to_anthropic(
    block: TextContent | ToolUseContent | ToolResultContent,
) -> dict[str, Any]:
    """Convert a content block to Anthropic format."""
    if isinstance(block, TextContent):
        return {"type": "text", "text": block.text}
    elif isinstance(block, ToolUseContent):
        return {
            "type": "tool_use",
            "id": block.id,
            "name": block.name,
            "input": block.input,
        }
    else:
        return {
            "type": "tool_result",
            "tool_use_id": block.tool_use_id,
            "content": block.content,
            "is_error": block.is_error,
        }


def convert_message_to_anthropic(msg: Message) -> dict[str, Any] | None:
    """Convert a single message to Anthropic format.

    Returns None for system messages (handled separately by Anthropic).
    """
    if msg.role == "system":
        return None

    if isinstance(msg.content, str):
        return {"role": msg.role, "content": msg.content}

    content_blocks = [convert_content_block_to_anthropic(block) for block in msg.content]
    return {"role": msg.role, "content": content_blocks}


def convert_messages_to_anthropic(messages: list[Message]) -> list[dict[str, Any]]:
    """Convert internal messages to Anthropic API format."""
    result = []
    for msg in messages:
        converted = convert_message_to_anthropic(msg)
        if converted is not None:
            result.append(converted)
    return result


def build_response(
    response_id: str,
    content: list[TextContent | ToolUseContent],
    stop_reason: str,
    input_tokens: int,
    output_tokens: int,
) -> Response:
    """Build a Response object with usage stats."""
    return Response(
        id=response_id,
        content=content,
        stop_reason=stop_reason,
        usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def convert_tools_to_openai(tools: list[dict[str, Any]] | list[Any]) -> list[dict[str, Any]]:
    """Convert tool schemas to OpenAI function format."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {}),
            },
        }
        for tool in tools
    ]


def map_openai_stop_reason(finish_reason: str | None) -> str:
    """Map OpenAI finish_reason to internal stop_reason."""
    if finish_reason == "tool_calls":
        return "tool_use"
    elif finish_reason == "stop":
        return "end_turn"
    return "end_turn"


def clean_schema_for_gemini(schema: dict[str, Any]) -> dict[str, Any]:
    """Clean JSON schema for Gemini compatibility.

    Removes unsupported keys like 'title', '$defs', 'definitions'.
    """
    clean = {k: v for k, v in schema.items() if k not in ("title", "$defs", "definitions")}
    if "properties" in clean:
        clean["properties"] = {
            k: clean_schema_for_gemini(v) for k, v in clean["properties"].items()
        }
    return clean
