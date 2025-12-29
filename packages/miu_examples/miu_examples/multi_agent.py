"""Multi-agent example demonstrating agent orchestration.

Run with:
    python -m miu_examples.multi_agent

Requires:
    ANTHROPIC_API_KEY environment variable

This example demonstrates:
    1. Creating specialized agents for different tasks
    2. Orchestrating agents to solve complex problems
    3. Passing context between agents
"""

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult


class ResearchInput(BaseModel):
    """Input for research agent."""

    topic: str = Field(description="Topic to research")


class WriteInput(BaseModel):
    """Input for writer agent."""

    topic: str = Field(description="Topic to write about")
    context: str = Field(description="Research context to use")


class ResearchTool(Tool):
    """Mock research tool that simulates gathering information."""

    name = "research"
    description = "Research a topic and gather relevant information."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return ResearchInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Simulate research (mock implementation)."""
        topic = kwargs.get("topic", "")

        # Mock research results
        research_data = {
            "ai": "AI is transforming industries. Key trends: LLMs, agents, multimodal.",
            "python": "Python is popular for ML/AI. Key libraries: PyTorch, TensorFlow, transformers.",
            "agents": "AI agents use LLMs for reasoning. Patterns: ReAct, chain-of-thought, tool use.",
        }

        topic_lower = topic.lower()
        for key, data in research_data.items():
            if key in topic_lower:
                return ToolResult(output=f"Research findings: {data}")

        return ToolResult(output=f"Research on '{topic}': General information gathered.")


class WriterTool(Tool):
    """Mock writer tool that generates content."""

    name = "write_article"
    description = "Write an article based on research."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return WriteInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Generate article (mock implementation)."""
        topic = kwargs.get("topic", "Unknown")
        context = kwargs.get("context", "")

        # Simple article generation
        article = f"""
# {topic.title()}

Based on our research: {context[:100]}...

## Key Points
- This is an automatically generated article
- Content is based on the research provided
- The topic covers {topic}

## Conclusion
This article provides an overview of {topic}.
"""
        return ToolResult(output=article.strip())


async def create_researcher() -> ReActAgent:
    """Create a research-focused agent."""
    provider = create_provider("anthropic:claude-sonnet-4-20250514")
    registry = ToolRegistry()
    registry.register(ResearchTool())

    return ReActAgent(
        provider=provider,
        tools=registry,
        config=AgentConfig(
            name="researcher",
            system_prompt=(
                "You are a research specialist. Use the research tool to gather "
                "information on topics. Summarize your findings clearly."
            ),
            max_iterations=3,
        ),
    )


async def create_writer() -> ReActAgent:
    """Create a writing-focused agent."""
    provider = create_provider("anthropic:claude-sonnet-4-20250514")
    registry = ToolRegistry()
    registry.register(WriterTool())

    return ReActAgent(
        provider=provider,
        tools=registry,
        config=AgentConfig(
            name="writer",
            system_prompt=(
                "You are a content writer. Use the provided research context "
                "to write engaging articles. Use the write_article tool."
            ),
            max_iterations=3,
        ),
    )


async def orchestrate(topic: str) -> str:
    """Orchestrate multiple agents to research and write about a topic."""
    print(f"Orchestrating agents for topic: {topic}\n")

    # Step 1: Research agent gathers information
    print("[Researcher] Gathering information...")
    researcher = await create_researcher()
    research_response = await researcher.run(f"Research the topic: {topic}")
    research_context = research_response.get_text()
    print(f"[Researcher] Done: {research_context[:100]}...\n")

    # Step 2: Writer agent creates content using research
    print("[Writer] Creating article...")
    writer = await create_writer()
    write_response = await writer.run(
        f"Write an article about {topic} using this research context: {research_context}"
    )
    article = write_response.get_text()
    print("[Writer] Done!\n")

    return article


async def main() -> None:
    """Run multi-agent orchestration example."""
    print("Multi-Agent Orchestration Example")
    print("=" * 40)

    # Example: Research and write about AI agents
    article = await orchestrate("AI Agents and their applications")

    print("Final Article:")
    print("-" * 40)
    print(article)


if __name__ == "__main__":
    asyncio.run(main())
