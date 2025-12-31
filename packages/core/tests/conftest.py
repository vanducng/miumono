"""Shared fixtures for core tests."""

import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from miu_core.memory import Memory, ShortTermMemory
from miu_core.models import (
    Message,
    MessageStopEvent,
    Response,
    StreamEvent,
    TextContent,
    TextDeltaEvent,
    ToolResultContent,
    ToolUseContent,
    Usage,
)
from miu_core.providers.base import LLMProvider, ToolSchema
from miu_core.tools import ToolContext, ToolRegistry, ToolResult


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""

    name = "mock"
    model = "mock-model"

    def __init__(
        self,
        response_text: str = "Mock response",
        stop_reason: str = "end_turn",
        tool_uses: list[ToolUseContent] | None = None,
    ) -> None:
        self.response_text = response_text
        self.stop_reason = stop_reason
        self.tool_uses = tool_uses or []
        self.call_count = 0
        self.last_messages: list[Message] = []

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Return mock response."""
        self.call_count += 1
        self.last_messages = messages

        content: list[TextContent | ToolUseContent] = []
        if self.response_text:
            content.append(TextContent(text=self.response_text))
        content.extend(self.tool_uses)

        return Response(
            id=f"mock-response-{self.call_count}",
            content=content,
            stop_reason=self.stop_reason,
            usage=Usage(input_tokens=100, output_tokens=50),
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamEvent]:
        """Stream mock response."""
        self.call_count += 1
        self.last_messages = messages

        if self.response_text:
            # Stream text in chunks
            words = self.response_text.split()
            for word in words:
                yield TextDeltaEvent(text=word + " ")

        yield MessageStopEvent(stop_reason=self.stop_reason)


@pytest.fixture
def mock_provider() -> MockProvider:
    """Create mock LLM provider for testing."""
    return MockProvider()


@pytest.fixture
def mock_provider_with_tools() -> MockProvider:
    """Create mock provider that returns tool use."""
    tool_use = ToolUseContent(
        id="tool-1",
        name="echo",
        input={"message": "test"},
    )
    return MockProvider(
        response_text="",
        stop_reason="tool_use",
        tool_uses=[tool_use],
    )


@pytest.fixture
def sample_messages() -> list[Message]:
    """Sample conversation messages."""
    return [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there!"),
        Message(role="user", content="How are you?"),
    ]


@pytest.fixture
def sample_tool_result() -> ToolResultContent:
    """Sample tool result content."""
    return ToolResultContent(
        tool_use_id="tool-1",
        content="Tool executed successfully",
        is_error=False,
    )


@pytest.fixture
def memory() -> Memory:
    """Create short-term memory for testing."""
    return ShortTermMemory()


@pytest.fixture
def memory_with_messages(memory: Memory, sample_messages: list[Message]) -> Memory:
    """Memory pre-populated with sample messages."""
    for msg in sample_messages:
        memory.add(msg)
    return memory


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create empty tool registry."""
    return ToolRegistry()


@pytest.fixture
def tool_context() -> ToolContext:
    """Create tool context with default values."""
    return ToolContext()


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def tool_context_with_dir(temp_dir: Path) -> ToolContext:
    """Create tool context with temp working directory."""
    return ToolContext(working_dir=str(temp_dir))


@pytest.fixture
def mock_tool_success() -> AsyncMock:
    """Create mock tool that returns success."""
    mock = AsyncMock()
    mock.execute.return_value = ToolResult(output="Success", success=True)
    return mock


@pytest.fixture
def mock_tool_failure() -> AsyncMock:
    """Create mock tool that returns failure."""
    mock = AsyncMock()
    mock.execute.return_value = ToolResult(
        output="Failed",
        success=False,
        error="Tool execution failed",
    )
    return mock
