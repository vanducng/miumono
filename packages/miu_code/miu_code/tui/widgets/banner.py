"""Animated welcome banner widget."""

import os
from typing import Any

from rich.text import Text
from textual.app import RenderResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widget import Widget

from miu_code.tui.theme import VIBE_COLORS, get_gradient_color

# ASCII art logo for miu
MIU_LOGO = r"""
           _
 _ __ ___ (_)_   _
| '_ ` _ \| | | | |
| | | | | | | |_| |
|_| |_| |_|_|\__,_|
"""

# Compact version with space for side info
MIU_LOGO_COMPACT = r"""
  _ __ ___ (_)_   _
 | '_ ` _ \| | | | |
 | | | | | | | |_| |
 |_| |_| |_|_|\__,_|
"""


class WelcomeBanner(Widget):
    """Animated welcome banner with color cascade effect."""

    DEFAULT_CSS = """
    WelcomeBanner {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
    }
    """

    animation_progress = reactive(0.0)
    _animation_complete = False
    _timer: Timer | None = None

    def __init__(
        self,
        version: str = "",
        model: str = "",
        mcp_count: int = 0,
        working_dir: str = "",
        compact: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.version = version
        self.model = model
        self.mcp_count = mcp_count
        self.working_dir = working_dir or os.getcwd()
        self.logo = MIU_LOGO_COMPACT if compact else MIU_LOGO
        self._lines = [line for line in self.logo.strip().split("\n") if line]
        self._compact = compact

    def _format_path(self, path: str) -> str:
        """Shorten path with ~ for home dir."""
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path

    def on_mount(self) -> None:
        """Start animation on mount."""
        self._start_animation()

    def _start_animation(self) -> None:
        """Start the color cascade animation."""
        self.animation_progress = 0.0
        self._animation_complete = False
        self._timer = self.set_interval(0.05, self._tick_animation)

    def _tick_animation(self) -> None:
        """Animation tick."""
        if self.animation_progress >= 1.0:
            self._animation_complete = True
            if self._timer:
                self._timer.stop()
            return
        self.animation_progress += 0.08

    def render(self) -> RenderResult:
        """Render the banner with animated colors and side info."""
        text = Text()

        # Build info lines for side panel
        info_lines = []
        if self.version:
            info_lines.append(f"Miu Code v{self.version}")
        if self.model:
            mcp_str = f" | {self.mcp_count} MCP" if self.mcp_count > 0 else ""
            info_lines.append(f"{self.model}{mcp_str}")
        if self.working_dir:
            info_lines.append(self._format_path(self.working_dir))

        # Render logo with side info
        for line_idx, line in enumerate(self._lines):
            # Render animated logo characters
            for char_idx, char in enumerate(line):
                line_delay = line_idx * 0.15
                char_delay = (char_idx / max(len(line), 1)) * 0.3
                char_progress = max(
                    0.0, min(1.0, (self.animation_progress - line_delay - char_delay) * 3)
                )

                if self._animation_complete:
                    color = VIBE_COLORS["gold"]
                else:
                    color = get_gradient_color(char_progress)

                text.append(char, style=f"bold {color}")

            # Add side info on corresponding lines (offset by 2 spaces)
            if self._compact and line_idx < len(info_lines):
                text.append("    ", style="")
                text.append(info_lines[line_idx], style=f"dim {VIBE_COLORS['orange_gold']}")

            text.append("\n")

        # Add help hint line
        text.append("\n")
        text.append("  Type /help for commands", style="dim white")
        text.append("  |  ", style="dim white")
        text.append("/model to switch", style="dim white")
        text.append("\n")

        # Add separator
        sep_width = 60
        text.append("  " + "─" * sep_width + "\n", style=f"dim {VIBE_COLORS['orange_gold']}")

        return text
