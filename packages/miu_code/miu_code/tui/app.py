"""Miu Code TUI Application - Vibe Inspired."""

import os
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

from miu_code.agent.coding import CodingAgent
from miu_code.tui.widgets.banner import WelcomeBanner
from miu_code.tui.widgets.chat import ChatLog
from miu_code.tui.widgets.chat_input import ChatInputContainer
from miu_code.tui.widgets.loading import LoadingSpinner
from miu_code.tui.widgets.messages import BashOutputMessage
from miu_core.models import (
    MessageStopEvent,
    TextDeltaEvent,
    ToolExecutingEvent,
    ToolResultEvent,
)
from miu_core.modes import ModeManager
from miu_core.paths import MiuPaths
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
        Binding("shift+tab", "cycle_mode", "Cycle Mode", show=False, priority=True),
        Binding("shift+up", "scroll_chat_up", "Scroll Up", show=False, priority=True),
        Binding("shift+down", "scroll_chat_down", "Scroll Down", show=False, priority=True),
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

        # Auto-scroll state
        self._auto_scroll = True

    def _format_path(self, path: str) -> str:
        """Format path for display (shorten home dir)."""
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path

    def _is_scrolled_to_bottom(self, scroll_view: VerticalScroll) -> bool:
        """Check if scroll view is at bottom (with threshold)."""
        try:
            threshold = 3
            return scroll_view.scroll_y >= (scroll_view.max_scroll_y - threshold)
        except Exception:
            return True

    def _scroll_to_bottom(self) -> None:
        """Scroll chat to bottom."""
        try:
            chat_area = self.query_one("#chat-area", VerticalScroll)
            chat_area.scroll_end(animate=False)
        except Exception:
            pass

    def _scroll_to_bottom_deferred(self) -> None:
        """Schedule scroll to bottom after refresh."""
        self.call_after_refresh(self._scroll_to_bottom)

    def action_scroll_chat_up(self) -> None:
        """Scroll chat up and disable auto-scroll."""
        try:
            chat_area = self.query_one("#chat-area", VerticalScroll)
            chat_area.scroll_relative(y=-5, animate=False)
            self._auto_scroll = False
        except Exception:
            pass

    def action_scroll_chat_down(self) -> None:
        """Scroll chat down, re-enable auto-scroll if at bottom."""
        try:
            chat_area = self.query_one("#chat-area", VerticalScroll)
            chat_area.scroll_relative(y=5, animate=False)
            if self._is_scrolled_to_bottom(chat_area):
                self._auto_scroll = True
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        """Create child widgets - Vibe-inspired layout."""
        # Get short model name for display
        model_short = self.model.split(":")[-1] if ":" in self.model else self.model

        # Chat area with scrollable banner (scrolls away like vibe)
        with VerticalScroll(id="chat-area"):
            yield WelcomeBanner(
                version=__version__,
                model=model_short,
                mcp_count=0,
                working_dir=self._working_dir,
                compact=True,
                id="banner",
            )
            yield ChatLog(id="chat", scroll_callback=self._scroll_to_bottom_deferred)

        # Loading indicator (outside scroll)
        yield LoadingSpinner(id="loading")

        # Bottom app container (for input/approval switching later)
        with Static(id="bottom-app-container"):
            yield ChatInputContainer(
                history_file=self._get_history_file(),
                id="input-container",
            )

        # Bottom bar: path left, mode indicator center, tokens right (always visible)
        with Horizontal(id="bottom-bar"):
            yield Static(self._format_path(self._working_dir), id="path-display")
            yield Static("", id="spacer")
            mode_text = f"{self._mode_manager.label} (shift+tab to cycle)"
            yield Static(mode_text, id="mode-indicator")
            yield Static(self._usage_tracker.format_usage(), id="token-display")

    def on_mount(self) -> None:
        """Initialize agent on mount."""
        self._init_agent()
        self.query_one("#input-container", ChatInputContainer).focus_input()

    def _get_history_file(self) -> Path:
        """Get history file path."""
        paths = MiuPaths.get()
        paths.ensure_dir(paths.code)
        return paths.history

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
        """Update token display in bottom bar."""
        token_display = self.query_one("#token-display", Static)
        token_display.update(self._usage_tracker.format_usage())

    def _update_mode_indicator(self) -> None:
        """Update mode indicator in bottom bar."""
        mode_indicator = self.query_one("#mode-indicator", Static)
        mode_text = f"{self._mode_manager.label} (shift+tab to cycle)"
        mode_indicator.update(mode_text)

    async def on_chat_input_container_submitted(self, event: ChatInputContainer.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        if not value:
            return

        # Handle ! prefix for bash
        if value.startswith("!"):
            await self._handle_bash_command(value[1:])
            return

        # Handle / prefix for commands (future)
        if value.startswith("/"):
            await self._handle_command(value)
            return

        # Regular message
        await self._handle_user_message(value)

    async def _handle_bash_command(self, command: str) -> None:
        """Execute bash command and display result."""
        import subprocess

        if not command:
            return

        chat = self.query_one("#chat", ChatLog)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False,
                timeout=30,
                cwd=self._working_dir,
            )
            stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
            stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
            output = stdout or stderr or "(no output)"

            bash_msg = BashOutputMessage(
                command=command,
                cwd=self._working_dir,
                output=output.strip(),
                exit_code=result.returncode,
            )
            chat.mount(bash_msg)
            self._scroll_to_bottom_deferred()

        except subprocess.TimeoutExpired:
            chat.add_error(f"Command timed out: {command}")
        except Exception as e:
            chat.add_error(f"Command failed: {e}")

    async def _handle_command(self, command: str) -> None:
        """Handle slash commands."""
        chat = self.query_one("#chat", ChatLog)
        chat.add_system_message(f"Command not implemented: {command}")

    async def _handle_user_message(self, query: str) -> None:
        """Handle regular user message with streaming."""
        if self._is_processing:
            return

        input_container = self.query_one("#input-container", ChatInputContainer)
        chat = self.query_one("#chat", ChatLog)
        chat.add_user_message(query)

        # Trigger scroll after user message
        self._scroll_to_bottom_deferred()

        if not self._agent:
            chat.add_error("Agent not initialized")
            return

        # Start loading animation
        loading = self.query_one("#loading", LoadingSpinner)
        loading.start()
        self._is_processing = True

        try:
            # Use streaming for real-time response
            await chat.start_streaming()
            chat_area = self.query_one("#chat-area", VerticalScroll)
            async for stream_event in self._agent.run_stream(query):
                # Track if we were at bottom before update
                was_at_bottom = self._is_scrolled_to_bottom(chat_area)

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

                # Scroll if was at bottom and auto-scroll enabled
                if was_at_bottom and self._auto_scroll:
                    self._scroll_to_bottom_deferred()

            await chat.end_streaming()
        except Exception as e:
            chat.add_error(str(e))
        finally:
            # Stop loading animation
            loading.stop()
            self._is_processing = False
            input_container.focus_input()

    def action_cycle_mode(self) -> None:
        """Cycle through agent modes."""
        self._mode_manager.cycle()
        self._update_mode_indicator()
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
