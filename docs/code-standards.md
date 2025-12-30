# Code Standards & Guidelines

**Project:** Miumono
**Version:** 0.1.0
**Last Updated:** 2025-12-29

## Overview

This document defines the code standards, patterns, and best practices for Miumono development. Compliance is enforced through automated tooling (Ruff, MyPy, Pytest) and code review.

## Python Version & Environment

- **Minimum Python:** 3.11
- **Target Python:** 3.11, 3.12, 3.13
- **Virtual Environment:** `.venv` (local), created by `uv sync`
- **Package Manager:** UV with workspace configuration

## Code Style & Formatting

### Ruff Configuration

**File:** `pyproject.toml` `[tool.ruff]` section

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["miu_core", "miu_code"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Formatting Rules

**Line Length:** 100 characters (excluding ignored E501 for exceptionally long lines)

**Indentation:** 4 spaces (never tabs)

**Quotes:** Double quotes for all strings
```python
# Good
message = "Hello, world!"
docstring = """Multi-line docstring."""

# Bad
message = 'Hello, world!'
docstring = '''Multi-line docstring.'''
```

**Imports:**
- Use isort-style grouping (stdlib, third-party, first-party, local)
- Alphabetical ordering within groups
- One import per line preferred for clarity
```python
# Good
import asyncio
from typing import Any

from pydantic import BaseModel

from miu_core.models import Message
from miu_code.tools import read_file
```

**Naming Conventions:**

| Type | Convention | Example |
|------|-----------|---------|
| Modules | snake_case | `agent_base.py`, `tool_registry.py` |
| Functions | snake_case | `get_provider()`, `execute_tool()` |
| Classes | PascalCase | `ReActAgent`, `AnthropicProvider` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| Private members | _leading_underscore | `_internal_state`, `_validate()` |
| Type variables | PascalCase | `T`, `ProviderType` |

**Blank Lines:**
- 2 blank lines between top-level functions/classes
- 1 blank line between methods in a class
- No blank lines between imports (before non-import code)

**Line Continuation:**
Prefer implicit continuation over backslash:
```python
# Good
result = (
    some_function(arg1, arg2) +
    another_function(arg3, arg4)
)

# Avoid
result = some_function(arg1, arg2) + \
    another_function(arg3, arg4)
```

## Type Safety & MyPy

### MyPy Configuration

**File:** `pyproject.toml` `[tool.mypy]` section

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]
explicit_package_bases = true
mypy_path = "packages/miu_core:packages/miu_code"
exclude = ["tests/"]
```

### Type Annotation Standards

**All Functions Must Be Typed:**
```python
# Good
def get_provider(name: str) -> Provider:
    """Get provider by name."""
    pass

async def execute_tool(
    tool: Tool,
    args: dict[str, Any],
) -> ToolResult:
    """Execute a tool with given arguments."""
    pass

# Bad - missing return type
def get_provider(name: str):
    pass

# Bad - untyped parameter
def execute_tool(tool, args: dict) -> ToolResult:
    pass
```

**Type Annotations for Complex Types:**
```python
from typing import Any, Optional

# Good
results: list[dict[str, Any]] = []
callback: Optional[Callable[[Message], None]] = None
provider_map: dict[str, type[Provider]] = {}

# Avoid
results = []  # Type unclear
callback = None  # Could be anything
provider_map = {}  # Type of values unclear
```

**Async Functions:**
```python
# Good
async def run_agent(query: str) -> str:
    """Run agent with query."""
    return await self._execute(query)

# Must specify return type
async def process_tools(tools: list[Tool]) -> list[ToolResult]:
    pass
```

**Generic Types:**
```python
from typing import Generic, TypeVar

T = TypeVar("T")
ProviderT = TypeVar("ProviderT", bound=BaseProvider)

class Registry(Generic[T]):
    """Generic registry for extensibility."""

    def register(self, name: str, item: T) -> None:
        pass

    def get(self, name: str) -> Optional[T]:
        pass
```

**No Type: Any Except When Necessary:**
```python
# Good - specific types
def parse_config(data: dict[str, str]) -> Config:
    pass

# Acceptable only when truly unknown
def handle_api_response(response: Any) -> dict[str, Any]:
    """Handle response from external API."""
    return json.loads(response)
```

## Code Organization

### Module Structure

**Package Layout:**
```
miu_core/
├── __init__.py           # Public API exports
├── agents/               # Agent implementations
│   ├── __init__.py       # Public exports
│   └── base.py           # Base agent class
├── models/               # Data models
│   ├── __init__.py
│   └── messages.py
├── providers/            # LLM provider integrations
│   ├── __init__.py
│   └── anthropic.py
├── tools/                # Tool abstractions
│   ├── __init__.py
│   ├── base.py
│   └── registry.py
└── version.py            # Version info
```

**File Naming:**
- Module files: lowercase with underscores (`agent_base.py`, `tool_registry.py`)
- Single responsibility: One main class/concept per file
- Tests: `test_<module_name>.py` in parallel structure

### Class Structure

```python
class ExampleClass:
    """One-line summary.

    More detailed description spanning multiple lines
    if needed. Explain what the class does, its purpose,
    and typical usage patterns.
    """

    # Class variables at top
    DEFAULT_TIMEOUT: int = 30

    def __init__(self, name: str, value: int) -> None:
        """Initialize the example class.

        Args:
            name: The identifier for this instance.
            value: The initial value.
        """
        self.name = name
        self.value = value

    def public_method(self) -> str:
        """Public method with clear documentation."""
        return f"{self.name}={self.value}"

    def _private_method(self) -> None:
        """Private methods prefixed with underscore."""
        pass

    @property
    def computed_property(self) -> int:
        """Property for computed attributes."""
        return self.value * 2
```

## Async/Await Patterns

### Async-First Design
- All I/O operations must be async (files, HTTP, subprocess)
- Use `asyncio` for concurrency
- Use `aiofiles` for file operations
- Use `httpx` for HTTP requests

```python
# Good - async file operations
async def read_file(path: str) -> str:
    """Read file asynchronously."""
    async with aiofiles.open(path, "r") as f:
        return await f.read()

# Good - async HTTP
async def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Good - concurrent operations
async def process_files(paths: list[str]) -> list[str]:
    """Process multiple files concurrently."""
    tasks = [read_file(path) for path in paths]
    return await asyncio.gather(*tasks)
```

### Error Handling in Async Code
```python
async def safe_operation() -> Optional[Result]:
    """Perform operation with error handling."""
    try:
        result = await self.fetch_data()
        return result
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

## TUI Widgets (Textual Framework)

### Widget Structure

All TUI widgets in `miu_code.tui.widgets` follow these standards:

**File Organization:**
```
miu_code/tui/widgets/
├── __init__.py         # Public exports (Widget.py names)
├── status.py           # StatusBar widget
├── banner.py           # WelcomeBanner widget
├── chat.py             # ChatLog widget
├── input.py            # MessageInput widget
└── loading.py          # LoadingSpinner widget
```

**Widget Naming:** Class names like `StatusBar`, `WelcomeBanner` (PascalCase with "Widget" suffix optional)

### Reactive Properties

Textual widgets use reactive properties for state management:

```python
from textual.widget import Widget
from textual.reactive import reactive

class CustomWidget(Widget):
    """Widget with reactive state."""

    # Declare reactive properties
    label: reactive[str] = reactive("default")
    value: reactive[int] = reactive(0)

    def render(self) -> RenderResult:
        """Render based on reactive properties."""
        return Text(f"{self.label}: {self.value}")
```

**Rules:**
- Use `reactive[Type]` type annotations for clarity
- Initialize reactive properties with default values
- Keep reactive properties simple (strings, ints, floats, bools)
- Use private attributes (`_attr`) for complex state

### Widget Integration Patterns

**With ModeManager:**
```python
from miu_core.modes import ModeManager, AgentMode

class StatusBar(Widget):
    """Status bar with mode management."""

    def __init__(
        self,
        mode_manager: ModeManager | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._mode_manager = mode_manager or ModeManager()

        # Subscribe to mode changes
        self._mode_manager.on_change(self._on_mode_change)

    def _on_mode_change(self, mode: AgentMode) -> None:
        """Handle mode change event."""
        # Update display when mode changes
        self.update_display()
```

**With UsageTracker:**
```python
from miu_core.usage import UsageTracker

class StatusBar(Widget):
    """Status bar with token usage tracking."""

    def __init__(
        self,
        usage_tracker: UsageTracker | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._usage_tracker = usage_tracker or UsageTracker()

    def update_usage(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        """Update token usage display."""
        self._usage_tracker.add_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
```

### Widget CSS

**DEFAULT_CSS Pattern:**
```python
class CustomWidget(Widget):
    """Widget with styling."""

    DEFAULT_CSS = """
    CustomWidget {
        dock: bottom;  # or: top, left, right
        height: auto;  # or: 100% or fixed number
        width: 100%;
        padding: 1 2;  # vertical horizontal
        background: $surface;
        color: $text;
    }
    """
```

**Color Palette:**
- Use Textual's built-in variables: `$surface`, `$text`, `$accent`, `$success`, `$error`
- Define custom colors in theme module (`miu_code/tui/theme.py`)
- Use inline styles in `render()` for dynamic colors

### Widget Testing (test_tui_widgets.py)

**Test Structure:**
```python
class TestStatusBar:
    """Tests for StatusBar widget."""

    def test_instantiation(self) -> None:
        """Test widget can be instantiated with defaults."""
        widget = StatusBar()
        assert widget is not None

    def test_with_custom_managers(self) -> None:
        """Test widget with injected dependencies."""
        manager = ModeManager()
        widget = StatusBar(mode_manager=manager)
        assert widget._mode_manager is manager

    def test_reactive_property_updates(self) -> None:
        """Test reactive properties update correctly."""
        widget = StatusBar()
        widget.label = "new value"
        assert widget.label == "new value"
```

**Testing Patterns:**
- Test instantiation with defaults and custom values
- Test reactive property updates
- Test integration with managers (ModeManager, UsageTracker)
- Test callback registration and invocation
- Test formatting/rendering logic (without full Textual harness)

## Error Handling

### Exception Hierarchy
Define custom exceptions at package level:
```python
# miu_core/exceptions.py
class MiuError(Exception):
    """Base exception for all miu errors."""
    pass

class ProviderError(MiuError):
    """LLM provider error."""
    pass

class ToolError(MiuError):
    """Tool execution error."""
    pass

class AgentError(MiuError):
    """Agent operation error."""
    pass
```

### Error Patterns
```python
# Good - specific exceptions
async def execute_tool(tool: Tool) -> ToolResult:
    try:
        return await tool.execute()
    except ProviderError as e:
        logger.error(f"Provider error: {e}")
        raise AgentError(f"Tool execution failed: {tool.name}") from e

# Good - validation
def validate_config(config: dict[str, Any]) -> None:
    if "api_key" not in config:
        raise ValueError("Missing required api_key in config")
```

## Testing Standards

### Test Structure

**File:** `packages/<package>/tests/test_<module>.py`

```python
import pytest

from miu_core.providers import AnthropicProvider


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    @pytest.fixture
    def provider(self) -> AnthropicProvider:
        """Create provider instance."""
        return AnthropicProvider(api_key="test-key")

    def test_initialization(self, provider: AnthropicProvider) -> None:
        """Test provider initializes correctly."""
        assert provider is not None

    @pytest.mark.asyncio
    async def test_execute_async(
        self,
        provider: AnthropicProvider,
    ) -> None:
        """Test async execution."""
        result = await provider.generate("test prompt")
        assert result is not None


# Parametrized tests
@pytest.mark.parametrize(
    "input,expected",
    [
        ("test", "test"),
        ("", ""),
        ("hello world", "hello world"),
    ],
)
def test_various_inputs(input: str, expected: str) -> None:
    """Test with various inputs."""
    assert process(input) == expected
```

### Testing Conventions

- **Coverage Target:** ≥80% per package
- **Async Tests:** Use `@pytest.mark.asyncio`
- **Mocking:** Use `unittest.mock` for external dependencies
- **Fixtures:** Reusable test fixtures for common setup
- **Naming:** `test_<function_name>` or `test_<scenario>`

## Documentation Standards

### Module Documentation
```python
"""Module for tool registry and management.

This module provides the core tool registry system that allows
agents to discover and execute tools. Tools can be registered
programmatically and accessed by name.

Typical usage:
    registry = ToolRegistry()
    registry.register("read_file", read_tool)
    tool = registry.get("read_file")
    result = await tool.execute(...)
"""
```

### Function/Method Documentation
```python
async def execute(
    self,
    tool_name: str,
    arguments: dict[str, Any],
) -> ToolResult:
    """Execute a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute.
        arguments: Arguments to pass to the tool.

    Returns:
        ToolResult containing output and metadata.

    Raises:
        ToolError: If tool not found or execution fails.

    Example:
        result = await registry.execute(
            "read_file",
            {"path": "/etc/config"},
        )
        print(result.output)
    """
```

### Documentation Elements
- One-line summary (imperative)
- Detailed description if complex
- Args section with types and descriptions
- Returns section with type and description
- Raises section listing exceptions
- Example section for non-obvious usage

## Security Considerations

### Input Validation
```python
from pathlib import Path

def validate_file_path(path: str) -> Path:
    """Validate and sanitize file path."""
    # Prevent directory traversal
    resolved = Path(path).resolve()
    base = Path.cwd().resolve()

    if not str(resolved).startswith(str(base)):
        raise ValueError(f"Path outside allowed directory: {path}")

    return resolved
```

### Environment Variables
```python
import os

# Good - use environment variables for secrets
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

# Bad - never hardcode credentials
api_key = "sk-1234567890"  # Don't do this!
```

## Performance Guidelines

### Async Best Practices
- Never block the event loop
- Use `asyncio.gather()` for concurrent operations
- Use timeouts on network operations
- Cache expensive computations

### Memory Management
```python
# Good - generator for large datasets
async def process_large_file(path: str) -> AsyncGenerator[str, None]:
    """Process file line by line."""
    async with aiofiles.open(path) as f:
        async for line in f:
            yield line.strip()

# Avoid - loading entire file into memory
async def bad_process_file(path: str) -> list[str]:
    async with aiofiles.open(path) as f:
        return (await f.read()).split("\n")
```

## Version & Release

### Version Format
Semantic Versioning: `MAJOR.MINOR.PATCH`
- `0.1.0` - MVP release
- `0.2.0` - Feature additions
- `1.0.0` - Stable release

**File:** `miu_core/version.py`

### Conventional Commits

All commits must follow Conventional Commits format to enable automated versioning via Release-Please:

**Format:** `<type>(<scope>): <subject>`

**Types:**
- `feat` - New feature (minor version bump)
- `fix` - Bug fix (patch version bump)
- `perf` - Performance improvement (shows in changelog)
- `refactor` - Code refactoring (hidden from changelog)
- `docs` - Documentation changes (hidden from changelog)
- `chore` - Maintenance, dependencies (hidden from changelog)

**Examples:**
```bash
# Feature
git commit -m "feat(agent): add streaming support"

# Bug fix
git commit -m "fix(tools): resolve file validation issue"

# Breaking change (major version bump)
git commit -m "feat(api): redesign provider interface

BREAKING CHANGE: Provider.execute() renamed to Provider.invoke()"
```

### PR Title Requirements

PR titles must follow Conventional Commits format (enforced by `pr-title-check` workflow). When PRs are squash-merged, the title becomes the commit message for automated versioning.

### Changelog
Automatically generated per-package via Release-Please:
- Generated from commit types and scopes
- One CHANGELOG.md per package in `packages/*/CHANGELOG.md`
- Sections: Features, Bug Fixes, Performance, Refactoring
- Includes commit links and contributor mentions

**See:** `docs/release-management.md` for Release-Please configuration

## Tools & Commands Reference

**Install & Sync:**
```bash
uv sync              # Install all dependencies
```

**Linting & Formatting:**
```bash
uv run ruff check .             # Check for violations
uv run ruff format .            # Auto-format code
```

**Type Checking:**
```bash
uv run mypy packages/           # Type check all packages
uv run mypy packages/miu_core   # Type check specific package
```

**Testing:**
```bash
uv run pytest                           # Run all tests
uv run pytest packages/miu_core         # Test specific package
uv run pytest --cov                     # With coverage report
uv run pytest -v packages/miu_code/tests/test_code_tools.py
```

**Combined Check:**
```bash
uv sync && \
uv run ruff check . && \
uv run ruff format . && \
uv run mypy packages/ && \
uv run pytest --cov
```

---

**Document Status:** ACTIVE
**Enforced By:** CI/CD Pipeline
**Last Review:** 2025-12-30
**Latest Addition:** TUI Widget standards (Phase 3)
