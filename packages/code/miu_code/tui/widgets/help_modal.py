"""Help modal widget for displaying commands and keyboard shortcuts."""

from typing import Any, ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Markdown

from miu_core.commands import Command, CommandRegistry


def generate_help_markdown(
    registry: CommandRegistry | None = None,
    is_tui: bool = False,
) -> str:
    """Generate help text as markdown.

    Args:
        registry: Command registry to get commands from
        is_tui: Whether generating for TUI (includes more shortcuts) or CLI

    Returns:
        Formatted markdown help text
    """
    sections = []

    # Title
    title = "# miu help\n" if is_tui else "# miu - AI coding agent\n"
    sections.append(title)

    # Keyboard shortcuts
    header = "## Keyboard Shortcuts\n" if is_tui else "## Keyboard Shortcuts (TUI mode)\n"
    sections.append(header)
    shortcuts = [
        ("Ctrl+C", "Quit application"),
        ("Ctrl+N", "Start new session"),
        ("Ctrl+L", "Clear chat history"),
        ("Escape", "Interrupt / Focus input"),
        ("Shift+Tab", "Cycle agent mode"),
    ]
    if is_tui:
        shortcuts.extend(
            [
                ("Shift+Up/Down", "Scroll chat"),
                ("Enter", "Send message"),
            ]
        )
    for key, desc in shortcuts:
        sections.append(f"- **{key}** - {desc}")
    sections.append("")

    # Built-in commands
    sections.append("## Built-in Commands\n")
    if registry:
        builtins = registry.list_builtins()
        for cmd in builtins:
            aliases_str = ""
            if cmd.aliases:
                clean_aliases = [a.lstrip("/") for a in cmd.aliases if a.lstrip("/") != cmd.name]
                if clean_aliases:
                    aliases_str = f" (aliases: {', '.join(clean_aliases)})"
            sections.append(f"- **/{cmd.name}**{aliases_str} - {cmd.description}")
    else:
        sections.append("- **/help** - Show this help")
        sections.append("- **/model** - Switch AI model")
        sections.append("- **/clear** - Clear conversation")
        sections.append("- **/exit** - Exit application")
    sections.append("")

    # Template commands
    if registry:
        templates: list[Command] = registry.list_commands()
        if templates:
            sections.append("## Slash Commands\n")
            for template_cmd in templates:
                hint = f" {template_cmd.argument_hint}" if template_cmd.argument_hint else ""
                sections.append(f"- **/{template_cmd.name}**{hint} - {template_cmd.description}")
            sections.append("")

    if is_tui:
        # Modes (TUI specific)
        sections.append("## Agent Modes\n")
        modes = [
            ("Normal", "Execute tools with approval for dangerous ops"),
            ("Ask", "All tool executions require approval"),
            ("Plan", "Planning mode - creates implementation plans"),
        ]
        for mode, desc in modes:
            sections.append(f"- **{mode}** - {desc}")
        sections.append("")

        # Tips
        sections.append("## Tips\n")
        sections.append("- Use `!command` to run shell commands directly")
        sections.append("- Type `/` followed by command name to use slash commands")
        sections.append("- Press ESC to close this help\n")
    else:
        # Usage (CLI specific)
        sections.append("## Usage\n")
        sections.append("- Type your message and press Enter to chat with the AI")
        sections.append("- Use `!command` to run shell commands directly")
        sections.append("- Use `/command` to run slash commands")
        sections.append("- Run `miu code` for interactive TUI mode\n")

    return "\n".join(sections)


class HelpModal(Container):
    """Modal overlay for displaying help content."""

    can_focus = True
    can_focus_children = False

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
    ]

    class Closed(Message):
        """Modal was closed."""

    DEFAULT_CSS = """
    HelpModal {
        width: 100%;
        height: auto;
        max-height: 24;
        background: $surface;
        border: round #666666;
        padding: 0 1;
        margin: 0 0 1 0;
    }
    HelpModal #help-content {
        width: 100%;
        height: auto;
        max-height: 22;
    }
    HelpModal Markdown {
        width: 100%;
        height: auto;
        padding: 0;
        margin: 0;
    }
    """

    def __init__(self, registry: CommandRegistry | None = None, **kwargs: Any) -> None:
        super().__init__(id="help-modal", **kwargs)
        self._registry = registry
        self._scroll_view: VerticalScroll | None = None

    def compose(self) -> ComposeResult:
        help_text = generate_help_markdown(self._registry, is_tui=True)
        with VerticalScroll(id="help-content"):
            yield Markdown(help_text)

    async def on_mount(self) -> None:
        self._scroll_view = self.query_one("#help-content", VerticalScroll)
        self.focus()

    def action_close(self) -> None:
        """Close the help modal."""
        self.post_message(self.Closed())

    def action_scroll_up(self) -> None:
        """Scroll content up."""
        if self._scroll_view:
            self._scroll_view.scroll_relative(y=-3, animate=False)

    def action_scroll_down(self) -> None:
        """Scroll content down."""
        if self._scroll_view:
            self._scroll_view.scroll_relative(y=3, animate=False)

    def on_blur(self, event: events.Blur) -> None:
        """Keep focus on help modal."""
        self.call_after_refresh(self.focus)
