"""Chat log widget with Vibe-inspired styling."""

from rich.markdown import Markdown
from rich.text import Text
from textual.widgets import RichLog

from miu_code.tui.theme import SEMANTIC_COLORS, VIBE_COLORS


class ChatLog(RichLog):
    """Rich log for displaying chat messages with enhanced styling."""

    def add_user_message(self, text: str) -> None:
        """Add a user message to the log."""
        user_text = Text()
        user_text.append("> ", style=f"bold {VIBE_COLORS['gold']}")
        user_text.append("You: ", style=f"bold {SEMANTIC_COLORS['user']}")
        user_text.append(text)
        self.write(user_text)
        self.write("")  # Spacing

    def add_assistant_message(self, text: str) -> None:
        """Add an assistant message to the log."""
        header = Text()
        header.append("◆ ", style=f"bold {VIBE_COLORS['orange']}")
        header.append("Agent", style=f"bold {SEMANTIC_COLORS['assistant']}")
        self.write(header)

        try:
            self.write(Markdown(text))
        except Exception:
            self.write(text)
        self.write("")  # Spacing

    def add_system_message(self, text: str) -> None:
        """Add a system message to the log."""
        sys_text = Text()
        sys_text.append("→ ", style=f"dim {VIBE_COLORS['orange_gold']}")
        sys_text.append(text, style=f"dim {SEMANTIC_COLORS['system']}")
        self.write(sys_text)

    def add_error(self, text: str) -> None:
        """Add an error message to the log."""
        err_text = Text()
        err_text.append("✗ ", style=f"bold {SEMANTIC_COLORS['error']}")
        err_text.append("Error: ", style=f"bold {SEMANTIC_COLORS['error']}")
        err_text.append(text, style=SEMANTIC_COLORS["error"])
        self.write(err_text)
        self.write("")  # Spacing

    def add_thinking_message(self, text: str) -> None:
        """Add a thinking/reasoning message to the log."""
        think_text = Text()
        think_text.append("◌ ", style=f"italic {SEMANTIC_COLORS['thinking']}")
        think_text.append(text, style=f"italic dim {SEMANTIC_COLORS['thinking']}")
        self.write(think_text)

    def add_tool_call(self, tool_name: str, args: str = "") -> None:
        """Add a tool call indicator to the log."""
        tool_text = Text()
        tool_text.append("⚡ ", style=f"bold {VIBE_COLORS['orange']}")
        tool_text.append("Calling: ", style="dim")
        tool_text.append(tool_name, style=f"bold {VIBE_COLORS['orange_gold']}")
        if args:
            tool_text.append(f" {args}", style="dim")
        self.write(tool_text)

    def add_tool_result(self, result: str, success: bool = True) -> None:
        """Add a tool result to the log."""
        color = SEMANTIC_COLORS["assistant"] if success else SEMANTIC_COLORS["error"]
        icon = "✓" if success else "✗"
        result_text = Text()
        result_text.append(f"  {icon} ", style=f"bold {color}")
        result_text.append(result, style=f"dim {color}")
        self.write(result_text)
