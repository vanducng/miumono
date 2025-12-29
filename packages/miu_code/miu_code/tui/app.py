"""Miu Code TUI Application - Vibe Inspired."""

import os
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical
from textual.widgets import Footer, Input

from miu_code.agent.coding import CodingAgent
from miu_code.tui.widgets.banner import WelcomeBanner
from miu_code.tui.widgets.chat import ChatLog
from miu_code.tui.widgets.loading import LoadingSpinner

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

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Get short model name for display
        model_short = self.model.split(":")[-1] if ":" in self.model else self.model

        yield WelcomeBanner(
            version=__version__,
            model=model_short,
            compact=True,
            id="banner",
        )
        yield Container(ChatLog(id="chat"), id="main")
        yield Vertical(
            LoadingSpinner(id="loading"),
            Input(placeholder="Ask anything... (Ctrl+C to quit)", id="input"),
            id="input-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize agent on mount."""
        self._init_agent()
        self.query_one("#input", Input).focus()

    def _init_agent(self) -> None:
        """Initialize the coding agent."""
        working_dir = os.getcwd()
        self._agent = CodingAgent(
            model=self.model,
            working_dir=working_dir,
            session_id=self.session_id,
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
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
            response = await self._agent.run(query)
            text = response.get_text()
            if text:
                chat.add_assistant_message(text)
        except Exception as e:
            chat.add_error(str(e))
        finally:
            # Stop loading animation
            loading.stop()
            self._is_processing = False
            input_widget.disabled = False
            input_widget.focus()

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
