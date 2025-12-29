"""ReAct (Reasoning + Acting) agent implementation."""

from miu_core.agents.base import Agent, AgentConfig
from miu_core.memory import Memory
from miu_core.models import Message, Response, TextContent, ToolResultContent
from miu_core.providers.base import LLMProvider
from miu_core.tools.base import ToolContext
from miu_core.tools.registry import ToolRegistry


class ReActAgent(Agent):
    """Agent implementing ReAct pattern."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: ToolRegistry | None = None,
        config: AgentConfig | None = None,
        memory: Memory | None = None,
        working_dir: str = ".",
    ) -> None:
        super().__init__(provider, tools, config, memory)
        self.working_dir = working_dir

    async def run(self, query: str) -> Response:
        """Execute ReAct loop for query."""
        self.memory.add(Message(role="user", content=query))

        # Auto-truncate if over context limit
        self.memory.truncate(self.config.max_context_tokens)

        for _ in range(self.config.max_iterations):
            response = await self.provider.complete(
                messages=self.memory.get_messages(),
                tools=self.tools.get_schemas() if len(self.tools) > 0 else None,
                system=self.config.system_prompt,
            )
            self.memory.add(Message(role="assistant", content=response.content))

            if response.stop_reason == "end_turn":
                return response

            if response.stop_reason == "tool_use":
                await self._execute_tools(response)

        return Response(
            id="max_iterations",
            content=[TextContent(text="Maximum iterations reached")],
            stop_reason="max_iterations",
        )

    async def _execute_tools(self, response: Response) -> None:
        """Execute tool calls from response."""
        tool_uses = response.get_tool_uses()
        ctx = ToolContext(working_dir=self.working_dir)

        results: list[ToolResultContent] = []
        for tool_use in tool_uses:
            result = await self.tools.execute(tool_use.name, ctx, **tool_use.input)
            results.append(
                ToolResultContent(
                    tool_use_id=tool_use.id,
                    content=result.output,
                    is_error=not result.success,
                )
            )

        self.memory.add(Message(role="user", content=results))
