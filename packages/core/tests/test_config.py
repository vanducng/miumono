"""Tests for miu_core.config module."""

import tempfile
from pathlib import Path

from miu_core.config import MiuConfig, StatusBarConfig


class TestStatusBarConfig:
    """Tests for StatusBarConfig dataclass."""

    def test_default_values(self) -> None:
        """Default config should have expected values."""
        config = StatusBarConfig()
        assert config.elements == ["path", "model", "tokens"]
        assert config.show_path is True
        assert config.show_model is True
        assert config.show_tokens is True
        assert config.separator == " │ "
        assert config.model_format == "short"

    def test_from_dict_with_all_values(self) -> None:
        """from_dict should parse all values correctly."""
        data = {
            "elements": ["model", "tokens"],
            "show_path": False,
            "show_model": True,
            "show_tokens": True,
            "separator": " | ",
            "model_format": "full",
        }
        config = StatusBarConfig.from_dict(data)
        assert config.elements == ["model", "tokens"]
        assert config.show_path is False
        assert config.separator == " | "
        assert config.model_format == "full"

    def test_from_dict_with_partial_values(self) -> None:
        """from_dict should use defaults for missing values."""
        data = {"show_model": False}
        config = StatusBarConfig.from_dict(data)
        assert config.show_model is False
        assert config.elements == ["path", "model", "tokens"]  # default
        assert config.separator == " │ "  # default


class TestMiuConfig:
    """Tests for MiuConfig loading."""

    def test_default_config(self) -> None:
        """Loading from non-existent file should return defaults."""
        config = MiuConfig.load(Path("/nonexistent/config.toml"))
        assert isinstance(config.statusbar, StatusBarConfig)
        assert config.statusbar.show_model is True

    def test_load_from_toml_file(self) -> None:
        """Should correctly load config from TOML file."""
        toml_content = b"""
[statusbar]
elements = ["tokens", "model"]
show_path = false
separator = " - "
model_format = "full"
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            config = MiuConfig.load(Path(f.name))

        assert config.statusbar.elements == ["tokens", "model"]
        assert config.statusbar.show_path is False
        assert config.statusbar.separator == " - "
        assert config.statusbar.model_format == "full"

    def test_load_with_invalid_toml_returns_defaults(self) -> None:
        """Invalid TOML should return default config instead of raising."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(b"this is not valid toml [[[")
            f.flush()
            config = MiuConfig.load(Path(f.name))

        # Should return defaults, not crash
        assert config.statusbar.show_model is True

    def test_get_default_config_content(self) -> None:
        """get_default_config_content should return valid TOML template."""
        content = MiuConfig.get_default_config_content()
        assert "[statusbar]" in content
        assert "elements" in content
        assert "model_format" in content
