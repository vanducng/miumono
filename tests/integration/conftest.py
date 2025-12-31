"""Shared fixtures for integration tests."""

import tempfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from miu_core.agents.base import AgentConfig
from miu_core.agents.react import ReActAgent
from miu_core.memory import ShortTermMemory
from miu_core.models import Response, TextContent
from miu_core.providers.base import LLMProvider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult


class EchoInput(BaseModel):
    message: str


class EchoTool(Tool):
    """Simple echo tool for integration testing."""

    name = "echo"
    description = "Echoes the input message"

    def get_input_schema(self) -> type[BaseModel]:
        return EchoInput

    async def execute(self, ctx: ToolContext, message: str, **kwargs: object) -> ToolResult:
        return ToolResult(output=f"Echo: {message}")


class MockProvider(LLMProvider):
    """Mock provider for integration testing."""

    name = "mock"
    model = "mock-model"

    def __init__(self, responses: list[Response] | None = None) -> None:
        self.responses = responses or []
        self.call_count = 0
        self.received_messages: list[Any] = []

    async def complete(
        self,
        messages,
        tools=None,
        system=None,
        max_tokens=4096,
    ) -> Response:
        self.received_messages.append(messages)
        if self.responses:
            response = self.responses[min(self.call_count, len(self.responses) - 1)]
        else:
            response = Response(
                id=f"mock-{self.call_count}",
                content=[TextContent(text="Mock response")],
                stop_reason="end_turn",
            )
        self.call_count += 1
        return response


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create tool registry with echo tool."""
    registry = ToolRegistry()
    registry.register(EchoTool())
    return registry


@pytest.fixture
def memory() -> ShortTermMemory:
    """Create fresh memory."""
    return ShortTermMemory()


@pytest.fixture
def mock_provider() -> MockProvider:
    """Create mock provider."""
    return MockProvider()


@pytest.fixture
def agent_config() -> AgentConfig:
    """Create default agent config."""
    return AgentConfig(
        name="test-agent",
        max_iterations=5,
        max_context_tokens=100_000,
    )


@pytest.fixture
def react_agent(
    mock_provider: MockProvider,
    tool_registry: ToolRegistry,
    memory: ShortTermMemory,
    agent_config: AgentConfig,
    temp_dir: Path,
) -> ReActAgent:
    """Create configured ReAct agent."""
    return ReActAgent(
        provider=mock_provider,
        tools=tool_registry,
        memory=memory,
        config=agent_config,
        working_dir=str(temp_dir),
    )
