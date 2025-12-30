"""Miu Code TUI Application - Vibe Inspired."""

import os
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical
from textual.widgets import Input

from miu_code.agent.coding import CodingAgent
from miu_code.tui.widgets.banner import WelcomeBanner
from miu_code.tui.widgets.chat import ChatLog
from miu_code.tui.widgets.loading import LoadingSpinner
from miu_code.tui.widgets.status import StatusBar
from miu_core.models import (
    MessageStopEvent,
    TextDeltaEvent,
    ToolExecutingEvent,
    ToolResultEvent,
)
from miu_core.modes import ModeManager
from miu_core.usage import UsageTracker

# Version for display
__version__ = "0.2.0"


class MiuCodeApp(App[None]):
    """Miu Code Terminal User Interface with Vibe-inspired design."""

    CSS_PATH = "app.tcss"
    TITLE = "miu"
    SUB_TITLE = ""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "new_session", "New"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("shift+tab", "cycle_mode", "Mode", show=True),
    ]

    def __init__(
        self,
        model: str = "anthropic:claude-sonnet-4-20250514",
        session_id: str | None = None,
    ) -> None:
        super().__init__()
        self.model = model
        self.session_id = session_id
        self._agent: CodingAgent | None = None
        self._is_processing = False

        # State managers
        self._mode_manager = ModeManager()
        self._usage_tracker = UsageTracker()
        self._working_dir = os.getcwd()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Get short model name for display
        model_short = self.model.split(":")[-1] if ":" in self.model else self.model

        yield WelcomeBanner(
            version=__version__,
            model=model_short,
            mcp_count=0,  # TODO: detect MCP servers
            working_dir=self._working_dir,
            compact=True,
            id="banner",
        )
        yield Container(ChatLog(id="chat"), id="main")
        yield Vertical(
            LoadingSpinner(id="loading"),
            Input(placeholder="Ask anything... (Ctrl+C to quit)", id="input"),
            id="input-container",
        )
        yield StatusBar(
            mode_manager=self._mode_manager,
            usage_tracker=self._usage_tracker,
            working_dir=self._working_dir,
            id="status",
        )
        # Footer removed - StatusBar replaces it

    def on_mount(self) -> None:
        """Initialize agent on mount."""
        self._init_agent()
        self.query_one("#input", Input).focus()

    def _init_agent(self) -> None:
        """Initialize the coding agent."""
        self._agent = CodingAgent(
            model=self.model,
            working_dir=self._working_dir,
            session_id=self.session_id,
        )
        # Reset usage on new agent
        self._usage_tracker.reset()
        self._update_status_usage()

    def _update_status_usage(self) -> None:
        """Update status bar token display."""
        status = self.query_one("#status", StatusBar)
        status.token_usage = self._usage_tracker.format_usage()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission with streaming."""
        query = event.value.strip()
        if not query:
            return

        if self._is_processing:
            return

        input_widget = self.query_one("#input", Input)
        input_widget.clear()

        chat = self.query_one("#chat", ChatLog)
        chat.add_user_message(query)

        if not self._agent:
            chat.add_error("Agent not initialized")
            return

        # Start loading animation
        loading = self.query_one("#loading", LoadingSpinner)
        loading.start()
        self._is_processing = True
        input_widget.disabled = True

        try:
            # Use streaming for real-time response
            await chat.start_streaming()
            async for stream_event in self._agent.run_stream(query):
                if isinstance(stream_event, TextDeltaEvent):
                    await chat.append_streaming(stream_event.text)
                elif isinstance(stream_event, ToolExecutingEvent):
                    chat.add_tool_call(stream_event.tool_name)
                elif isinstance(stream_event, ToolResultEvent):
                    chat.add_tool_result(stream_event.output, stream_event.success)
                elif isinstance(stream_event, MessageStopEvent):
                    # Update usage from stop event
                    if stream_event.usage:
                        self._usage_tracker.add_usage(
                            input_tokens=stream_event.usage.get("input_tokens", 0),
                            output_tokens=stream_event.usage.get("output_tokens", 0),
                        )
                        self._update_status_usage()
            await chat.end_streaming()
        except Exception as e:
            chat.add_error(str(e))
        finally:
            # Stop loading animation
            loading.stop()
            self._is_processing = False
            input_widget.disabled = False
            input_widget.focus()

    def action_cycle_mode(self) -> None:
        """Cycle through agent modes."""
        self._mode_manager.cycle()
        chat = self.query_one("#chat", ChatLog)
        chat.add_system_message(f"Switched to {self._mode_manager.label}")

    def action_new_session(self) -> None:
        """Start a new session."""
        self.session_id = None
        self._init_agent()
        chat = self.query_one("#chat", ChatLog)
        chat.clear()
        chat.add_system_message("Started new session")

    def action_clear_chat(self) -> None:
        """Clear the chat log."""
        chat = self.query_one("#chat", ChatLog)
        chat.clear()


def run(model: str = "anthropic:claude-sonnet-4-20250514") -> None:
    """Run the TUI application."""
    app = MiuCodeApp(model=model)
    app.run()


if __name__ == "__main__":
    run()
