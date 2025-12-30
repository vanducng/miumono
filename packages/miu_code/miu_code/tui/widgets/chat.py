"""Chat log widget with Vibe-inspired styling and streaming support."""

from collections.abc import Callable
from typing import Any

from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Markdown, Static

from miu_code.tui.theme import SEMANTIC_COLORS, VIBE_COLORS


class MessageHeader(Static):
    """Header for a chat message."""

    def __init__(self, role: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.role = role

    def on_mount(self) -> None:
        """Set header content based on role."""
        header = Text()
        if self.role == "user":
            header.append("> ", style=f"bold {VIBE_COLORS['gold']}")
            header.append("You", style=f"bold {SEMANTIC_COLORS['user']}")
        elif self.role == "assistant":
            header.append("◆ ", style=f"bold {VIBE_COLORS['orange']}")
            header.append("Agent", style=f"bold {SEMANTIC_COLORS['assistant']}")
        elif self.role == "system":
            header.append("→ ", style=f"dim {VIBE_COLORS['orange_gold']}")
            header.append("System", style=f"dim {SEMANTIC_COLORS['system']}")
        elif self.role == "error":
            header.append("✗ ", style=f"bold {SEMANTIC_COLORS['error']}")
            header.append("Error", style=f"bold {SEMANTIC_COLORS['error']}")
        elif self.role == "tool":
            header.append("⚡ ", style=f"bold {VIBE_COLORS['orange']}")
            header.append("Tool", style=f"bold {VIBE_COLORS['orange_gold']}")
        self.update(header)


class ChatLog(VerticalScroll):
    """Scrollable chat log with streaming support."""

    DEFAULT_CSS = """
    ChatLog {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    ChatLog > MessageHeader {
        height: auto;
        margin-top: 1;
    }
    ChatLog > Markdown {
        height: auto;
        margin-left: 2;
        margin-bottom: 1;
    }
    ChatLog > Static.message-text {
        height: auto;
        margin-left: 2;
        margin-bottom: 1;
    }
    ChatLog > Static.tool-info {
        height: auto;
        margin-left: 2;
    }
    """

    def __init__(self, scroll_callback: Callable[[], None] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._streaming_md: Markdown | None = None
        self._stream: Any = None
        self._streaming_text = ""
        self._scroll_callback = scroll_callback

    def _notify_scroll(self) -> None:
        """Notify parent to scroll."""
        if self._scroll_callback:
            self._scroll_callback()

    def clear(self) -> None:
        """Clear all messages from the chat log."""
        self.remove_children()

    def add_user_message(self, text: str) -> None:
        """Add a user message to the log."""
        self.mount(MessageHeader("user"))
        msg = Static(text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_assistant_message(self, text: str) -> None:
        """Add a complete assistant message to the log."""
        self.mount(MessageHeader("assistant"))
        md = Markdown(text)
        self.mount(md)
        self._notify_scroll()

    async def start_streaming(self) -> None:
        """Start a streaming assistant message."""
        self._streaming_text = ""
        self.mount(MessageHeader("assistant"))
        self._streaming_md = Markdown("")
        self.mount(self._streaming_md)
        self._stream = Markdown.get_stream(self._streaming_md)
        self._notify_scroll()

    async def append_streaming(self, chunk: str) -> None:
        """Append text to streaming message."""
        self._streaming_text += chunk
        if self._stream:
            await self._stream.write(chunk)
        self._notify_scroll()

    async def end_streaming(self) -> None:
        """Finalize streaming message."""
        if self._stream:
            await self._stream.stop()
        self._stream = None
        self._streaming_md = None
        self._streaming_text = ""
        self._notify_scroll()

    def add_system_message(self, text: str) -> None:
        """Add a system message to the log."""
        sys_text = Text()
        sys_text.append("→ ", style=f"dim {VIBE_COLORS['orange_gold']}")
        sys_text.append(text, style=f"dim {SEMANTIC_COLORS['system']}")
        msg = Static(sys_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_error(self, text: str) -> None:
        """Add an error message to the log."""
        self.mount(MessageHeader("error"))
        err_text = Text()
        err_text.append(text, style=SEMANTIC_COLORS["error"])
        msg = Static(err_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_thinking_message(self, text: str) -> None:
        """Add a thinking/reasoning message to the log."""
        think_text = Text()
        think_text.append("◌ ", style=f"italic {SEMANTIC_COLORS['thinking']}")
        think_text.append(text, style=f"italic dim {SEMANTIC_COLORS['thinking']}")
        msg = Static(think_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_tool_call(self, tool_name: str, args: str = "") -> None:
        """Add a tool call indicator to the log."""
        tool_text = Text()
        tool_text.append("⚡ ", style=f"bold {VIBE_COLORS['orange']}")
        tool_text.append("Calling: ", style="dim")
        tool_text.append(tool_name, style=f"bold {VIBE_COLORS['orange_gold']}")
        if args:
            tool_text.append(f" {args}", style="dim")
        msg = Static(tool_text, classes="tool-info")
        self.mount(msg)
        self._notify_scroll()

    def add_tool_result(self, result: str, success: bool = True) -> None:
        """Add a tool result to the log."""
        color = SEMANTIC_COLORS["assistant"] if success else SEMANTIC_COLORS["error"]
        icon = "✓" if success else "✗"
        result_text = Text()
        result_text.append(f"  {icon} ", style=f"bold {color}")
        # Truncate long results
        display_result = result[:100] + "..." if len(result) > 100 else result
        result_text.append(display_result, style=f"dim {color}")
        msg = Static(result_text, classes="tool-info")
        self.mount(msg)
        self._notify_scroll()
