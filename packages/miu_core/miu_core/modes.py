"""Agent mode management."""

from collections.abc import Callable
from enum import Enum


class AgentMode(Enum):
    """Agent operation modes."""

    NORMAL = "normal"  # Execute immediately
    PLAN = "plan"  # Research, plan, then execute
    ASK = "ask"  # Always ask before actions


# Mode display configuration
MODE_CONFIG = {
    AgentMode.NORMAL: {"label": "normal", "icon": ""},
    AgentMode.PLAN: {"label": "plan mode", "icon": ""},
    AgentMode.ASK: {"label": "ask mode", "icon": ""},
}

# Mode cycle order
MODE_ORDER = [AgentMode.NORMAL, AgentMode.PLAN, AgentMode.ASK]


class ModeManager:
    """Manage agent mode state."""

    def __init__(self, initial: AgentMode = AgentMode.NORMAL) -> None:
        self._mode = initial
        self._on_change: list[Callable[[AgentMode], None]] = []

    @property
    def mode(self) -> AgentMode:
        """Current mode."""
        return self._mode

    @mode.setter
    def mode(self, value: AgentMode) -> None:
        """Set mode and notify listeners."""
        if value != self._mode:
            self._mode = value
            for callback in self._on_change:
                callback(value)

    def cycle(self) -> AgentMode:
        """Cycle to next mode, return new mode."""
        idx = MODE_ORDER.index(self._mode)
        next_idx = (idx + 1) % len(MODE_ORDER)
        self.mode = MODE_ORDER[next_idx]
        return self._mode

    def on_change(self, callback: Callable[[AgentMode], None]) -> None:
        """Register mode change callback."""
        self._on_change.append(callback)

    @property
    def label(self) -> str:
        """Display label for current mode."""
        return MODE_CONFIG[self._mode]["label"]

    @property
    def icon(self) -> str:
        """Icon for current mode."""
        return MODE_CONFIG[self._mode]["icon"]

    def format_status(self) -> str:
        """Format for status bar: 'plan mode (shift+tab to cycle)'."""
        return f"{self.icon} {self.label} (shift+tab to cycle)"
