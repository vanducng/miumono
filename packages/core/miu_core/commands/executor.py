"""Command executor for parsing and expanding slash commands."""

from dataclasses import dataclass
from enum import Enum, auto

from miu_core.commands.builtins import BuiltinCommand
from miu_core.commands.registry import CommandRegistry
from miu_core.commands.schema import Command


class CommandType(Enum):
    """Type of command being executed."""

    TEMPLATE = auto()  # Expands to prompt for LLM
    BUILTIN = auto()  # Executes handler directly


@dataclass
class CommandResult:
    """Result of command parsing/execution."""

    command_type: CommandType
    command_name: str
    args: str
    expanded: str | None = None  # For template commands
    handler: str | None = None  # For built-in commands
    exits: bool = False  # For built-in commands that exit app


class CommandExecutor:
    """Execute slash commands by parsing and expanding templates."""

    def __init__(self, registry: CommandRegistry) -> None:
        """Initialize executor with command registry.

        Args:
            registry: Registry containing available commands
        """
        self.registry = registry

    def parse(self, input_str: str) -> tuple[str, str] | None:
        """Parse '/command args' format.

        Args:
            input_str: Input string to parse

        Returns:
            Tuple of (command_name, args) or None if not a command
        """
        if not input_str.startswith("/"):
            return None

        stripped = input_str[1:].strip()
        if not stripped:
            return None

        parts = stripped.split(maxsplit=1)
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        return (command_name, args)

    def expand(self, command_name: str, args: str) -> str:
        """Expand command template with arguments.

        Args:
            command_name: Name of the command (without /)
            args: Arguments to pass to the command

        Returns:
            Expanded command content

        Raises:
            ValueError: If command not found or is a built-in
        """
        command = self.registry.get_template(command_name)
        if not command:
            raise ValueError(f"Unknown template command: /{command_name}")
        return command.expand(args)

    def execute(self, input_str: str) -> str | None:
        """Parse and expand a template command string.

        For backwards compatibility. Use resolve() for full command info.

        Args:
            input_str: Input string that may be a command

        Returns:
            Expanded command content or None if not a command/is builtin

        Raises:
            ValueError: If command not found
        """
        parsed = self.parse(input_str)
        if not parsed:
            return None

        command_name, args = parsed

        # Skip built-ins (they don't expand)
        if self.registry.is_builtin(command_name):
            return None

        return self.expand(command_name, args)

    def resolve(self, input_str: str) -> CommandResult | None:
        """Resolve a command to its full details.

        Args:
            input_str: Input string that may be a command

        Returns:
            CommandResult with type and details, or None if not a command

        Raises:
            ValueError: If command not found
        """
        parsed = self.parse(input_str)
        if not parsed:
            return None

        command_name, args = parsed
        command = self.registry.get(command_name)

        if not command:
            raise ValueError(f"Unknown command: /{command_name}")

        if isinstance(command, BuiltinCommand):
            return CommandResult(
                command_type=CommandType.BUILTIN,
                command_name=command.name,
                args=args,
                handler=command.handler,
                exits=command.exits,
            )
        elif isinstance(command, Command):
            return CommandResult(
                command_type=CommandType.TEMPLATE,
                command_name=command.name,
                args=args,
                expanded=command.expand(args),
            )

        return None

    def is_command(self, input_str: str) -> bool:
        """Check if input is a slash command.

        Args:
            input_str: Input to check

        Returns:
            True if input starts with /
        """
        return input_str.strip().startswith("/")

    def is_builtin(self, input_str: str) -> bool:
        """Check if input is a built-in command.

        Args:
            input_str: Input to check

        Returns:
            True if input is a built-in command
        """
        parsed = self.parse(input_str)
        if not parsed:
            return False
        return self.registry.is_builtin(parsed[0])
