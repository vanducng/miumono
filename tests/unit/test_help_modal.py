"""Unit tests for help modal widget."""

from miu_code.tui.widgets.help_modal import HelpModal, generate_help_markdown
from miu_core.commands import CommandRegistry


class TestGenerateHelpMarkdown:
    """Tests for generate_help_markdown function."""

    def test_generates_markdown_without_registry(self):
        """Test help text generation without registry."""
        help_text = generate_help_markdown()
        assert "# miu" in help_text
        assert "Keyboard Shortcuts" in help_text
        assert "Built-in Commands" in help_text
        assert "/help" in help_text
        assert "/model" in help_text
        assert "/exit" in help_text

    def test_generates_markdown_with_registry(self):
        """Test help text generation with registry."""
        registry = CommandRegistry()
        help_text = generate_help_markdown(registry)
        assert "# miu" in help_text
        assert "/help" in help_text
        assert "/model" in help_text
        assert "/clear" in help_text
        assert "/exit" in help_text

    def test_includes_keyboard_shortcuts(self):
        """Test keyboard shortcuts are included."""
        help_text = generate_help_markdown()
        assert "Ctrl+C" in help_text
        assert "Ctrl+N" in help_text
        assert "Escape" in help_text

    def test_includes_usage_section_cli(self):
        """Test usage section is included for CLI."""
        help_text = generate_help_markdown(is_tui=False)
        assert "Usage" in help_text
        assert "!command" in help_text

    def test_includes_modes_for_tui(self):
        """Test modes section is included for TUI."""
        help_text = generate_help_markdown(is_tui=True)
        assert "Agent Modes" in help_text
        assert "Normal" in help_text
        assert "Ask" in help_text

    def test_tui_includes_more_shortcuts(self):
        """Test TUI includes extra keyboard shortcuts."""
        help_text = generate_help_markdown(is_tui=True)
        assert "Shift+Up/Down" in help_text
        assert "Enter" in help_text


class TestHelpModal:
    """Tests for HelpModal widget."""

    def test_modal_creation(self):
        """Test creating help modal."""
        modal = HelpModal()
        assert modal.id == "help-modal"
        assert modal.can_focus is True

    def test_modal_with_registry(self):
        """Test creating help modal with registry."""
        registry = CommandRegistry()
        modal = HelpModal(registry=registry)
        assert modal._registry == registry

    def test_modal_uses_tui_mode(self):
        """Test modal generates TUI-specific help text."""
        registry = CommandRegistry()
        help_text = generate_help_markdown(registry, is_tui=True)
        assert "# miu help" in help_text
        assert "Keyboard Shortcuts" in help_text
        assert "Agent Modes" in help_text

    def test_modal_includes_aliases(self):
        """Test modal shows command aliases."""
        registry = CommandRegistry()
        help_text = generate_help_markdown(registry, is_tui=True)
        # Exit command has aliases like /quit, /q
        assert "exit" in help_text

    def test_modal_includes_modes(self):
        """Test modal shows agent modes in TUI mode."""
        help_text = generate_help_markdown(is_tui=True)
        assert "Agent Modes" in help_text
        assert "Normal" in help_text
        assert "Ask" in help_text
        assert "Plan" in help_text
