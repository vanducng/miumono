"""CLI entry point."""

import asyncio
import os

import asyncclick as click
from rich.console import Console
from rich.markdown import Markdown

from miu_code.agent.coding import CodingAgent

console = Console()


@click.command()
@click.argument("query", required=False)
@click.option(
    "--model",
    "-m",
    default="anthropic:claude-sonnet-4-20250514",
    help="Model to use (provider:model, e.g. openai:gpt-4o, google:gemini-2.0-flash)",
)
@click.option("--session", "-s", default=None, help="Session ID for persistence")
async def cli(query: str | None, model: str, session: str | None) -> None:
    """miu - AI coding agent.

    Run with a query for one-shot execution, or without for interactive REPL.

    Examples:
        miu "read pyproject.toml"
        miu --model openai:gpt-4o "hello"
        miu -m google:gemini-2.0-flash "list files"
    """
    working_dir = os.getcwd()
    agent = CodingAgent(model=model, working_dir=working_dir, session_id=session)

    if query:
        response = await agent.run(query)
        text = response.get_text()
        if text:
            console.print(Markdown(text))
    else:
        console.print("[bold blue]miu[/] - AI coding agent")
        console.print("Type /exit or /quit to exit\n")

        while True:
            try:
                user_input = await click.prompt("miu", prompt_suffix="> ")
                if user_input.strip() in ("/exit", "/quit"):
                    break
                if not user_input.strip():
                    continue

                response = await agent.run(user_input)
                text = response.get_text()
                if text:
                    console.print(Markdown(text))
                console.print()
            except (KeyboardInterrupt, EOFError):
                break

        console.print("\nGoodbye!")


def main() -> None:
    """Main entry point."""
    asyncio.run(cli())
