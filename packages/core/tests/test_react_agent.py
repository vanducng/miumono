"""Tests for ReAct agent implementation."""

import pytest
from pydantic import BaseModel

from miu_core.agents.base import AgentConfig
from miu_core.agents.react import ReActAgent
from miu_core.memory import ShortTermMemory
from miu_core.models import (
    Message,
    MessageStopEvent,
    Response,
    TextContent,
    TextDeltaEvent,
    ToolResultContent,
    ToolUseContent,
)
from miu_core.providers.base import LLMProvider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult


class EchoInput(BaseModel):
    message: str


class EchoTool(Tool):
    """Simple echo tool for testing."""

    name = "echo"
    description = "Echoes the input message"

    def get_input_schema(self) -> type[BaseModel]:
        return EchoInput

    async def execute(self, ctx: ToolContext, message: str, **kwargs: object) -> ToolResult:
        return ToolResult(output=f"Echo: {message}")


class FailingTool(Tool):
    """Tool that always fails for testing error handling."""

    name = "failing"
    description = "Always fails"

    def get_input_schema(self) -> type[BaseModel]:
        return EchoInput

    async def execute(self, ctx: ToolContext, **kwargs: object) -> ToolResult:
        raise ValueError("Intentional failure")


class TestReActAgentBasic:
    """Basic ReAct agent tests."""

    @pytest.mark.asyncio
    async def test_simple_query_no_tools(self, mock_provider: LLMProvider) -> None:
        """Test agent handles simple query without tools."""
        agent = ReActAgent(provider=mock_provider)
        response = await agent.run("Hello")

        assert response.get_text() == "Mock response"
        assert mock_provider.call_count == 1

    @pytest.mark.asyncio
    async def test_agent_adds_user_message_to_memory(self, mock_provider: LLMProvider) -> None:
        """Test agent adds user query to memory."""
        memory = ShortTermMemory()
        agent = ReActAgent(provider=mock_provider, memory=memory)

        await agent.run("Test query")

        messages = memory.get_messages()
        assert len(messages) >= 1
        assert messages[0].role == "user"
        assert "Test query" in str(messages[0].content)

    @pytest.mark.asyncio
    async def test_agent_adds_assistant_response_to_memory(
        self, mock_provider: LLMProvider
    ) -> None:
        """Test agent adds assistant response to memory."""
        memory = ShortTermMemory()
        agent = ReActAgent(provider=mock_provider, memory=memory)

        await agent.run("Test")

        messages = memory.get_messages()
        assert len(messages) >= 2
        assert messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_agent_respects_max_iterations(self) -> None:
        """Test agent stops at max iterations."""

        # Create provider that always returns tool_use
        class AlwaysToolProvider(LLMProvider):
            name = "always-tool"
            model = "test"
            call_count = 0

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                self.call_count += 1
                return Response(
                    id=f"resp-{self.call_count}",
                    content=[ToolUseContent(id="t1", name="echo", input={"message": "hi"})],
                    stop_reason="tool_use",
                )

        provider = AlwaysToolProvider()
        registry = ToolRegistry()
        registry.register(EchoTool())

        config = AgentConfig(max_iterations=3)
        agent = ReActAgent(provider=provider, tools=registry, config=config)

        response = await agent.run("Keep calling tools")

        assert response.stop_reason == "max_iterations"
        assert provider.call_count == 3


class TestReActAgentWithTools:
    """Tests for ReAct agent with tool execution."""

    @pytest.mark.asyncio
    async def test_agent_executes_tool(self) -> None:
        """Test agent executes tool and continues."""
        call_count = [0]

        class ToolThenEndProvider(LLMProvider):
            name = "tool-then-end"
            model = "test"

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                call_count[0] += 1
                if call_count[0] == 1:
                    return Response(
                        id="resp-1",
                        content=[ToolUseContent(id="t1", name="echo", input={"message": "test"})],
                        stop_reason="tool_use",
                    )
                else:
                    return Response(
                        id="resp-2",
                        content=[TextContent(text="Done with echo")],
                        stop_reason="end_turn",
                    )

        provider = ToolThenEndProvider()
        registry = ToolRegistry()
        registry.register(EchoTool())

        agent = ReActAgent(provider=provider, tools=registry)
        response = await agent.run("Use echo tool")

        assert response.get_text() == "Done with echo"
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_tool_result_added_to_memory(self) -> None:
        """Test tool results are added to memory."""

        class SingleToolProvider(LLMProvider):
            name = "single-tool"
            model = "test"
            call_count = 0

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                self.call_count += 1
                if self.call_count == 1:
                    return Response(
                        id="resp-1",
                        content=[ToolUseContent(id="t1", name="echo", input={"message": "hello"})],
                        stop_reason="tool_use",
                    )
                return Response(
                    id="resp-2",
                    content=[TextContent(text="Done")],
                    stop_reason="end_turn",
                )

        provider = SingleToolProvider()
        registry = ToolRegistry()
        registry.register(EchoTool())
        memory = ShortTermMemory()

        agent = ReActAgent(provider=provider, tools=registry, memory=memory)
        await agent.run("Echo something")

        messages = memory.get_messages()
        # Should have: user query, assistant tool_use, user tool_result, assistant done
        assert len(messages) >= 3

        # Check tool result was added
        tool_result_found = False
        for msg in messages:
            if msg.role == "user" and isinstance(msg.content, list):
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        tool_result_found = True
                        assert "Echo: hello" in content.content
        assert tool_result_found

    @pytest.mark.asyncio
    async def test_agent_handles_tool_failure(self) -> None:
        """Test agent handles tool execution failure gracefully."""

        class UseFailingToolProvider(LLMProvider):
            name = "use-failing"
            model = "test"
            call_count = 0

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                self.call_count += 1
                if self.call_count == 1:
                    return Response(
                        id="resp-1",
                        content=[ToolUseContent(id="t1", name="failing", input={"message": "x"})],
                        stop_reason="tool_use",
                    )
                return Response(
                    id="resp-2",
                    content=[TextContent(text="Handled error")],
                    stop_reason="end_turn",
                )

        provider = UseFailingToolProvider()
        registry = ToolRegistry()
        registry.register(FailingTool())

        agent = ReActAgent(provider=provider, tools=registry)
        response = await agent.run("Try failing tool")

        # Agent should continue after tool failure
        assert response.get_text() == "Handled error"


class TestReActAgentStreaming:
    """Tests for ReAct agent streaming."""

    @pytest.mark.asyncio
    async def test_stream_simple_response(self, mock_provider: LLMProvider) -> None:
        """Test streaming a simple response."""
        agent = ReActAgent(provider=mock_provider)

        events = []
        async for event in agent.run_stream("Hello"):
            events.append(event)

        # Should have text deltas and stop event
        assert len(events) > 0
        assert any(isinstance(e, TextDeltaEvent) for e in events)
        assert isinstance(events[-1], MessageStopEvent)

    @pytest.mark.asyncio
    async def test_stream_collects_text(self, mock_provider: LLMProvider) -> None:
        """Test streaming collects complete text."""
        agent = ReActAgent(provider=mock_provider)

        collected = ""
        async for event in agent.run_stream("Hello"):
            if isinstance(event, TextDeltaEvent):
                collected += event.text

        # Should have collected all text
        assert len(collected) > 0


class TestReActAgentConfig:
    """Tests for ReAct agent configuration."""

    @pytest.mark.asyncio
    async def test_custom_system_prompt(self, mock_provider: LLMProvider) -> None:
        """Test agent uses custom system prompt."""
        config = AgentConfig(system_prompt="You are a helpful assistant")
        agent = ReActAgent(provider=mock_provider, config=config)

        await agent.run("Hello")

        # Provider should have been called with the query
        assert mock_provider.call_count == 1

    @pytest.mark.asyncio
    async def test_custom_working_dir(self, mock_provider: LLMProvider) -> None:
        """Test agent uses custom working directory."""
        agent = ReActAgent(provider=mock_provider, working_dir="/custom/path")

        assert agent.working_dir == "/custom/path"

    @pytest.mark.asyncio
    async def test_context_truncation(self, mock_provider: LLMProvider) -> None:
        """Test memory truncation on long contexts."""
        config = AgentConfig(max_context_tokens=100)
        memory = ShortTermMemory()

        # Add many messages to exceed limit
        for i in range(50):
            memory.add(Message(role="user", content=f"Message {i} " * 10))
            memory.add(Message(role="assistant", content=f"Response {i} " * 10))

        agent = ReActAgent(provider=mock_provider, config=config, memory=memory)
        await agent.run("Final query")

        # Should still work despite long history
        assert mock_provider.call_count == 1


class TestReActAgentEdgeCases:
    """Edge case tests for ReAct agent."""

    @pytest.mark.asyncio
    async def test_empty_tool_registry(self, mock_provider: LLMProvider) -> None:
        """Test agent works with empty tool registry."""
        registry = ToolRegistry()
        agent = ReActAgent(provider=mock_provider, tools=registry)

        response = await agent.run("Hello")
        assert response.get_text() == "Mock response"

    @pytest.mark.asyncio
    async def test_none_tool_registry(self, mock_provider: LLMProvider) -> None:
        """Test agent works with None tool registry."""
        agent = ReActAgent(provider=mock_provider, tools=None)

        response = await agent.run("Hello")
        assert response.get_text() == "Mock response"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self) -> None:
        """Test agent handles multiple tool calls in one response."""

        class MultiToolProvider(LLMProvider):
            name = "multi-tool"
            model = "test"
            call_count = 0

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                self.call_count += 1
                if self.call_count == 1:
                    return Response(
                        id="resp-1",
                        content=[
                            ToolUseContent(id="t1", name="echo", input={"message": "one"}),
                            ToolUseContent(id="t2", name="echo", input={"message": "two"}),
                        ],
                        stop_reason="tool_use",
                    )
                return Response(
                    id="resp-2",
                    content=[TextContent(text="Both done")],
                    stop_reason="end_turn",
                )

        provider = MultiToolProvider()
        registry = ToolRegistry()
        registry.register(EchoTool())
        memory = ShortTermMemory()

        agent = ReActAgent(provider=provider, tools=registry, memory=memory)
        response = await agent.run("Call two tools")

        assert response.get_text() == "Both done"

        # Check both results in memory
        messages = memory.get_messages()
        tool_results = []
        for msg in messages:
            if msg.role == "user" and isinstance(msg.content, list):
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        tool_results.append(content)

        assert len(tool_results) == 2
        assert "Echo: one" in tool_results[0].content
        assert "Echo: two" in tool_results[1].content
