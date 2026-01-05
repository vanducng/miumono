"""Decorator-based tool definitions.

This module provides a decorator-based approach for defining tools,
inspired by FastMCP's @tool pattern. Tools can be defined as simple
async functions with type hints, and the decorator handles schema
generation and registration automatically.

Example:
    from miu_core.tools.decorators import tool

    @tool(description="Read a file's contents")
    async def read_file(file_path: str, encoding: str = "utf-8") -> str:
        '''Read file contents and return as string.'''
        with open(file_path, encoding=encoding) as f:
            return f.read()

    # Register with a registry
    registry = ToolRegistry()
    registry.register(read_file)
"""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, get_type_hints

from pydantic import BaseModel, Field, create_model

from miu_core.tools.base import Tool, ToolContext, ToolResult


def _get_type_mapping(python_type: type[Any]) -> type[Any]:
    """Map Python types to JSON-compatible types for schema generation."""
    type_map: dict[type[Any], type[Any]] = {
        str: str,
        int: int,
        float: float,
        bool: bool,
        list: list,
        dict: dict,
    }
    origin: type[Any] | None = getattr(python_type, "__origin__", None)
    if origin is not None:
        return origin
    result = type_map.get(python_type)
    return result if result is not None else object


def _create_input_model(func: Callable[..., Any], name: str) -> type[BaseModel]:
    """Create a Pydantic model from function signature.

    Args:
        func: The function to analyze
        name: Name for the generated model

    Returns:
        A Pydantic BaseModel class with fields matching function parameters
    """
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    fields: dict[str, Any] = {}
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls", "ctx"):
            continue

        param_type = hints.get(param_name, Any)
        has_default = param.default is not inspect.Parameter.empty

        if has_default:
            fields[param_name] = (param_type, Field(default=param.default))
        else:
            fields[param_name] = (param_type, ...)

    return create_model(f"{name}Input", **fields)


class FunctionTool(Tool):
    """Tool implementation wrapping a decorated function."""

    name: str
    description: str

    def __init__(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Initialize function-based tool.

        Args:
            func: The async function to wrap
            name: Tool name (defaults to function name)
            description: Tool description (defaults to docstring)
        """
        self._func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or f"Execute {self.name}"
        self._input_model = _create_input_model(func, self.name)

    def get_input_schema(self) -> type[BaseModel]:
        """Return Pydantic model for tool input."""
        return self._input_model

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Execute the wrapped function."""
        try:
            sig = inspect.signature(self._func)
            if "ctx" in sig.parameters:
                result = await self._func(ctx=ctx, **kwargs)
            else:
                result = await self._func(**kwargs)

            if isinstance(result, ToolResult):
                return result

            return ToolResult(output=str(result))
        except Exception as e:
            return ToolResult(
                output=str(e),
                success=False,
                error=str(e),
            )


def tool(
    name: str | None = None,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], FunctionTool]:
    """Decorator to create a tool from an async function.

    This decorator transforms an async function into a Tool that can be
    registered with a ToolRegistry. Type hints are used to generate the
    input schema automatically.

    Args:
        name: Override the tool name (defaults to function name)
        description: Override the description (defaults to docstring)

    Returns:
        Decorator that converts function to FunctionTool

    Example:
        @tool(description="Add two numbers together")
        async def add(a: int, b: int) -> int:
            '''Add a and b.'''
            return a + b

        # The tool can be registered and used:
        registry = ToolRegistry()
        registry.register(add)
    """

    def decorator(func: Callable[..., Any]) -> FunctionTool:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Tool '{func.__name__}' must be an async function")

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        tool_instance = FunctionTool(
            func=func,
            name=name,
            description=description,
        )

        wrapper._tool = tool_instance  # type: ignore[attr-defined]
        return tool_instance

    return decorator


def sync_tool(
    name: str | None = None,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], FunctionTool]:
    """Decorator to create a tool from a sync function.

    Similar to @tool but for synchronous functions. The function
    will be wrapped to be compatible with the async tool interface.

    Args:
        name: Override the tool name (defaults to function name)
        description: Override the description (defaults to docstring)

    Returns:
        Decorator that converts function to FunctionTool
    """
    import asyncio

    def decorator(func: Callable[..., Any]) -> FunctionTool:
        if inspect.iscoroutinefunction(func):
            raise TypeError(f"Tool '{func.__name__}' is async, use @tool instead")

        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

        async_wrapper.__name__ = func.__name__
        async_wrapper.__doc__ = func.__doc__
        async_wrapper.__annotations__ = func.__annotations__

        return FunctionTool(
            func=async_wrapper,
            name=name,
            description=description,
        )

    return decorator
