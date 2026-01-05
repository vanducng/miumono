"""Command registry for managing slash commands."""

from collections.abc import Iterator
from pathlib import Path

from miu_core.commands.builtins import BuiltinCommand, get_default_builtins
from miu_core.commands.schema import Command, parse_command_file


class CommandRegistry:
    """Registry for managing slash commands.

    Supports two types of commands:
    - Template commands: Expand to prompts sent to LLM
    - Built-in commands: Execute handlers directly
    """

    def __init__(self, load_builtins: bool = True) -> None:
        self._commands: dict[str, Command] = {}
        self._builtins: dict[str, BuiltinCommand] = {}
        self._alias_map: dict[str, str] = {}  # Maps alias -> command name

        if load_builtins:
            for builtin in get_default_builtins():
                self.register_builtin(builtin)

    def register(self, command: Command) -> None:
        """Register a template command.

        Args:
            command: Command to register
        """
        self._commands[command.name] = command

    def register_builtin(self, command: BuiltinCommand) -> None:
        """Register a built-in command.

        Args:
            command: BuiltinCommand to register
        """
        self._builtins[command.name] = command
        # Map all aliases to this command
        for alias in command.aliases:
            # Strip leading / if present
            clean_alias = alias.lstrip("/")
            self._alias_map[clean_alias] = command.name

    def get(self, name: str) -> Command | BuiltinCommand | None:
        """Get a command by name (template or built-in).

        Args:
            name: Command name (without leading /)

        Returns:
            Command or BuiltinCommand if found, None otherwise
        """
        # Check alias map first for built-ins
        if name in self._alias_map:
            builtin_name = self._alias_map[name]
            return self._builtins.get(builtin_name)

        # Check built-ins by name
        if name in self._builtins:
            return self._builtins[name]

        # Fall back to template commands
        return self._commands.get(name)

    def get_builtin(self, name: str) -> BuiltinCommand | None:
        """Get a built-in command by name or alias.

        Args:
            name: Command name or alias (without leading /)

        Returns:
            BuiltinCommand if found, None otherwise
        """
        if name in self._alias_map:
            return self._builtins.get(self._alias_map[name])
        return self._builtins.get(name)

    def get_template(self, name: str) -> Command | None:
        """Get a template command by name.

        Args:
            name: Command name (without leading /)

        Returns:
            Command if found, None otherwise
        """
        return self._commands.get(name)

    def is_builtin(self, name: str) -> bool:
        """Check if command is a built-in.

        Args:
            name: Command name (without leading /)

        Returns:
            True if built-in command
        """
        return name in self._builtins or name in self._alias_map

    def load_from_file(self, path: Path) -> Command | None:
        """Load a command from a markdown file.

        Args:
            path: Path to command file

        Returns:
            Loaded command or None if failed
        """
        if not path.exists() or path.suffix != ".md":
            return None

        content = path.read_text(encoding="utf-8")
        frontmatter, body = parse_command_file(content)

        command = Command(
            name=path.stem,
            description=frontmatter.get("description", ""),
            argument_hint=frontmatter.get("argument-hint", ""),
            content=body,
            source_path=path,
        )
        self.register(command)
        return command

    def load_from_directory(self, path: Path) -> int:
        """Load all commands from a directory.

        Args:
            path: Directory path containing command files

        Returns:
            Number of commands loaded
        """
        if not path.is_dir():
            return 0

        count = 0
        for file_path in path.glob("*.md"):
            if self.load_from_file(file_path):
                count += 1
        return count

    def list_commands(self) -> list[Command]:
        """Get all registered template commands.

        Returns:
            List of all template commands
        """
        return list(self._commands.values())

    def list_builtins(self) -> list[BuiltinCommand]:
        """Get all registered built-in commands.

        Returns:
            List of all built-in commands
        """
        return list(self._builtins.values())

    def list_all(self) -> list[Command | BuiltinCommand]:
        """Get all registered commands (both types).

        Returns:
            List of all commands (built-ins first, then templates)
        """
        return list(self._builtins.values()) + list(self._commands.values())

    def __len__(self) -> int:
        return len(self._commands) + len(self._builtins)

    def __iter__(self) -> Iterator[Command | BuiltinCommand]:
        yield from self._builtins.values()
        yield from self._commands.values()

    def __contains__(self, name: str) -> bool:
        return name in self._commands or name in self._builtins or name in self._alias_map
