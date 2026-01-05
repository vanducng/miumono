"""Unit tests for slash command system."""

import pytest

from miu_core.commands import (
    BuiltinCommand,
    Command,
    CommandExecutor,
    CommandRegistry,
    CommandResult,
    CommandType,
    get_default_builtins,
)


class TestBuiltinCommand:
    """Tests for BuiltinCommand dataclass."""

    def test_builtin_command_creation(self):
        """Test creating a built-in command."""
        cmd = BuiltinCommand(
            name="test",
            description="Test command",
            handler="_test_handler",
        )
        assert cmd.name == "test"
        assert cmd.description == "Test command"
        assert cmd.handler == "_test_handler"
        assert cmd.aliases == frozenset()
        assert cmd.exits is False

    def test_builtin_command_with_aliases(self):
        """Test built-in command with aliases."""
        cmd = BuiltinCommand(
            name="exit",
            description="Exit app",
            handler="_exit",
            aliases=frozenset(["/exit", "/quit", "/q"]),
            exits=True,
        )
        assert "/exit" in cmd.aliases
        assert "/quit" in cmd.aliases
        assert cmd.exits is True

    def test_get_default_builtins(self):
        """Test getting default built-in commands."""
        builtins = get_default_builtins()
        assert len(builtins) == 4
        names = {cmd.name for cmd in builtins}
        assert names == {"help", "model", "clear", "exit"}


class TestCommandRegistry:
    """Tests for CommandRegistry."""

    def test_registry_loads_builtins_by_default(self):
        """Test registry loads built-ins on init."""
        registry = CommandRegistry()
        assert len(registry.list_builtins()) == 4
        assert registry.is_builtin("help")
        assert registry.is_builtin("model")

    def test_registry_skip_builtins(self):
        """Test registry can skip loading built-ins."""
        registry = CommandRegistry(load_builtins=False)
        assert len(registry.list_builtins()) == 0

    def test_register_template_command(self):
        """Test registering a template command."""
        registry = CommandRegistry(load_builtins=False)
        cmd = Command(name="test", content="Test $ARGUMENTS")
        registry.register(cmd)
        assert registry.get_template("test") == cmd
        assert not registry.is_builtin("test")

    def test_register_builtin_command(self):
        """Test registering a built-in command."""
        registry = CommandRegistry(load_builtins=False)
        cmd = BuiltinCommand(
            name="custom",
            description="Custom command",
            handler="_custom",
            aliases=frozenset(["/custom", "/c"]),
        )
        registry.register_builtin(cmd)
        assert registry.get_builtin("custom") == cmd
        assert registry.get_builtin("c") == cmd  # Via alias
        assert registry.is_builtin("custom")
        assert registry.is_builtin("c")

    def test_get_returns_both_types(self):
        """Test get() returns both template and built-in commands."""
        registry = CommandRegistry()
        # Built-in
        assert registry.get("help") is not None
        # Add template
        cmd = Command(name="cook", content="Cook $ARGUMENTS")
        registry.register(cmd)
        assert registry.get("cook") == cmd

    def test_list_all(self):
        """Test list_all() returns both types."""
        registry = CommandRegistry()
        cmd = Command(name="test", content="Test")
        registry.register(cmd)
        all_cmds = registry.list_all()
        # 4 builtins + 1 template
        assert len(all_cmds) == 5

    def test_contains(self):
        """Test __contains__ checks all command types."""
        registry = CommandRegistry()
        assert "help" in registry
        assert "nonexistent" not in registry
        cmd = Command(name="cook", content="Cook")
        registry.register(cmd)
        assert "cook" in registry

    def test_iter(self):
        """Test __iter__ yields all commands."""
        registry = CommandRegistry()
        cmd = Command(name="test", content="Test")
        registry.register(cmd)
        all_cmds = list(registry)
        assert len(all_cmds) == 5


class TestCommandExecutor:
    """Tests for CommandExecutor."""

    @pytest.fixture
    def executor(self):
        """Create executor with registry containing both command types."""
        registry = CommandRegistry()
        # Add template command
        registry.register(Command(name="cook", content="Cook: $ARGUMENTS"))
        return CommandExecutor(registry)

    def test_parse_valid_command(self, executor):
        """Test parsing valid command."""
        result = executor.parse("/cook some args")
        assert result == ("cook", "some args")

    def test_parse_command_no_args(self, executor):
        """Test parsing command without args."""
        result = executor.parse("/help")
        assert result == ("help", "")

    def test_parse_not_command(self, executor):
        """Test parsing non-command returns None."""
        assert executor.parse("not a command") is None
        assert executor.parse("") is None

    def test_is_command(self, executor):
        """Test is_command detection."""
        assert executor.is_command("/help")
        assert executor.is_command("/cook test")
        assert not executor.is_command("not a command")

    def test_is_builtin(self, executor):
        """Test is_builtin detection."""
        assert executor.is_builtin("/help")
        assert executor.is_builtin("/q")  # Alias for exit
        assert not executor.is_builtin("/cook")
        assert not executor.is_builtin("help")

    def test_execute_template_command(self, executor):
        """Test execute() expands template commands."""
        result = executor.execute("/cook my task")
        assert result == "Cook: my task"

    def test_execute_builtin_returns_none(self, executor):
        """Test execute() returns None for built-ins."""
        result = executor.execute("/help")
        assert result is None

    def test_execute_unknown_command(self, executor):
        """Test execute() raises for unknown commands."""
        # Since unknown is not builtin, execute() tries to expand and fails
        with pytest.raises(ValueError, match="Unknown template command"):
            executor.execute("/unknown")

    def test_resolve_builtin_command(self, executor):
        """Test resolve() for built-in command."""
        result = executor.resolve("/help")
        assert result is not None
        assert result.command_type == CommandType.BUILTIN
        assert result.command_name == "help"
        assert result.handler == "_show_help"
        assert result.expanded is None

    def test_resolve_template_command(self, executor):
        """Test resolve() for template command."""
        result = executor.resolve("/cook my task")
        assert result is not None
        assert result.command_type == CommandType.TEMPLATE
        assert result.command_name == "cook"
        assert result.expanded == "Cook: my task"
        assert result.handler is None

    def test_resolve_builtin_alias(self, executor):
        """Test resolve() with builtin alias."""
        result = executor.resolve("/q")
        assert result is not None
        assert result.command_type == CommandType.BUILTIN
        assert result.command_name == "exit"
        assert result.exits is True

    def test_resolve_unknown_command(self, executor):
        """Test resolve() raises for unknown command."""
        with pytest.raises(ValueError, match="Unknown command"):
            executor.resolve("/unknown")

    def test_resolve_not_command(self, executor):
        """Test resolve() returns None for non-command."""
        assert executor.resolve("not a command") is None


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_template_result(self):
        """Test CommandResult for template command."""
        result = CommandResult(
            command_type=CommandType.TEMPLATE,
            command_name="cook",
            args="my task",
            expanded="Cook: my task",
        )
        assert result.command_type == CommandType.TEMPLATE
        assert result.expanded == "Cook: my task"
        assert result.handler is None
        assert result.exits is False

    def test_builtin_result(self):
        """Test CommandResult for built-in command."""
        result = CommandResult(
            command_type=CommandType.BUILTIN,
            command_name="exit",
            args="",
            handler="_exit_app",
            exits=True,
        )
        assert result.command_type == CommandType.BUILTIN
        assert result.handler == "_exit_app"
        assert result.exits is True
        assert result.expanded is None
