"""Configuration management for miu packages.

Provides dataclasses and loaders for user configuration from ~/.miu/config.toml.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StatusBarElement:
    """Single status bar element configuration."""

    name: str  # element identifier: path, model, tokens, mode
    visible: bool = True
    format: str = ""  # custom format string (element-specific)


@dataclass
class StatusBarConfig:
    """Status bar configuration.

    Controls layout, visibility, and formatting of status bar elements.
    Default layout: [path] [spacer] [model] [separator] [tokens]
    """

    # Element order (left to right)
    elements: list[str] = field(default_factory=lambda: ["path", "model", "tokens"])

    # Element visibility
    show_path: bool = True
    show_model: bool = True
    show_tokens: bool = True

    # Formatting
    separator: str = " │ "  # between elements
    model_format: str = "short"  # "short" (glm-4.7) or "full" (zai:glm-4.7)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatusBarConfig":
        """Create from dictionary (parsed TOML section)."""
        return cls(
            elements=data.get("elements", ["path", "model", "tokens"]),
            show_path=data.get("show_path", True),
            show_model=data.get("show_model", True),
            show_tokens=data.get("show_tokens", True),
            separator=data.get("separator", " │ "),
            model_format=data.get("model_format", "short"),
        )


@dataclass
class MiuConfig:
    """Main configuration container."""

    statusbar: StatusBarConfig = field(default_factory=StatusBarConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "MiuConfig":
        """Load configuration from TOML file.

        Args:
            config_path: Path to config file. If None, uses MiuPaths.config.

        Returns:
            Loaded configuration with defaults for missing values.
        """
        if config_path is None:
            from miu_core.paths import MiuPaths

            config_path = MiuPaths.get().config

        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            statusbar_data = data.get("statusbar", {})
            return cls(
                statusbar=StatusBarConfig.from_dict(statusbar_data),
            )
        except Exception:
            # Return defaults on any parse error
            return cls()

    @classmethod
    def get_default_config_content(cls) -> str:
        """Generate default config.toml content for reference."""
        return """# Miu Configuration File
# Location: ~/.miu/config.toml

[statusbar]
# Elements to display (left to right): path, model, tokens
elements = ["path", "model", "tokens"]

# Visibility toggles
show_path = true
show_model = true
show_tokens = true

# Separator between elements
separator = " │ "

# Model name format: "short" (glm-4.7) or "full" (zai:glm-4.7)
model_format = "short"
"""
