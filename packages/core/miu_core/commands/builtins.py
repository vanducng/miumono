"""Built-in commands that execute handlers directly."""

from dataclasses import dataclass, field


@dataclass
class BuiltinCommand:
    """Built-in command with handler reference.

    Unlike template commands that expand to prompts, built-in commands
    execute handler methods directly in the application.
    """

    name: str
    description: str
    handler: str  # Method name to call (e.g., "_show_help")
    aliases: frozenset[str] = field(default_factory=frozenset)
    exits: bool = False  # Whether command exits the application


# Default built-in commands
BUILTIN_COMMANDS: list[BuiltinCommand] = [
    BuiltinCommand(
        name="help",
        description="Show help message with commands and shortcuts",
        handler="_show_help",
        aliases=frozenset(["/help", "/?"]),
    ),
    BuiltinCommand(
        name="model",
        description="Switch between AI models",
        handler="_show_model_selector",
        aliases=frozenset(["/model", "/m"]),
    ),
    BuiltinCommand(
        name="clear",
        description="Clear conversation history",
        handler="_clear_history",
        aliases=frozenset(["/clear", "/cls"]),
    ),
    BuiltinCommand(
        name="exit",
        description="Exit the application",
        handler="_exit_app",
        aliases=frozenset(["/exit", "/quit", "/q"]),
        exits=True,
    ),
]


def get_default_builtins() -> list[BuiltinCommand]:
    """Get list of default built-in commands.

    Returns:
        List of BuiltinCommand instances
    """
    return list(BUILTIN_COMMANDS)
