# Code Standards & Guidelines

**Project:** Miumono
**Version:** 0.1.0
**Last Updated:** 2026-01-01

## Overview

This document defines the code standards, patterns, and best practices for Miumono development. Compliance is enforced through automated tooling (Ruff, MyPy, Pytest) and code review.

## Python Version & Environment

- **Minimum Python:** 3.11
- **Target Python:** 3.11, 3.12, 3.13
- **Virtual Environment:** `.venv` (local), created by `uv sync`
- **Package Manager:** UV with workspace configuration

### Timezone-Aware Datetime (Python 3.12+)

Use `datetime.now(UTC)` for timezone-aware UTC timestamps (Phase 02 compatibility):

```python
from datetime import UTC, datetime

# Good - UTC timezone aware (Python 3.12+)
timestamp = datetime.now(UTC)
datetime_field: datetime = Field(default_factory=lambda: datetime.now(UTC))

# Avoid - naive datetime (no timezone)
timestamp = datetime.now()  # Not timezone aware

# Also acceptable - datetime.utcnow() still works
import datetime as dt
timestamp = dt.datetime.utcnow()  # Deprecated but works
```

**Used in:**
- `miu_core.logging.types.LogEntry` (timestamp field)
- `miu_core.logging.session_logger.SessionLogger` (session timestamps)
- `miu_studio.models.api.SessionMessage` (message timestamps)
- `miu_studio.services.chat_service.ChatService` (message timestamps)
- `miu_studio.services.session_manager.SessionManager` (session timestamps)

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

## Type Safety & MyPy (Phase 03)

### py.typed Markers (Phase 03)

All packages include `py.typed` marker files to indicate they are type-checked:

**Locations:**
- `packages/core/miu_core/py.typed`
- `packages/code/miu_code/py.typed`
- `packages/studio/miu_studio/py.typed`

These empty marker files signal to type checkers that the package includes inline type annotations and is safe for use with strict type checking. When consumers install these packages, their type checkers will use our type information.

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

**Type Checking Command:**
```bash
# Type check all packages
uv run mypy packages/

# Type check specific package
uv run mypy packages/miu_core

# With detailed output
uv run mypy packages/ --show-error-codes --pretty
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
│   ├── converters.py     # Shared conversion utilities (Phase 04)
│   └── anthropic.py
├── session/              # Session storage abstraction (Phase 04)
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   └── jsonl.py          # JSONL implementation
├── memory/               # Memory management
│   ├── __init__.py
│   └── truncation.py     # Token-aware truncation (Phase 04)
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

## DRY Refactoring & Shared Utilities (Phase 04)

### Provider Converters

The `miu_core.providers.converters` module provides shared conversion utilities to eliminate duplication across provider implementations:

**Key Functions:**

```python
# Convert content blocks to provider-specific formats
def convert_content_block_to_anthropic(
    block: TextContent | ToolUseContent | ToolResultContent
) -> dict[str, Any]:
    """Convert content block to Anthropic API format."""

# Convert messages to provider format (filters system messages)
def convert_message_to_anthropic(msg: Message) -> dict[str, Any] | None:
    """Returns None for system messages (Anthropic handles separately)."""

def convert_messages_to_anthropic(messages: list[Message]) -> list[dict[str, Any]]:
    """Batch convert messages to Anthropic format."""

# Build Response objects with usage stats
def build_response(
    response_id: str,
    content: list[TextContent | ToolUseContent],
    stop_reason: str,
    input_tokens: int,
    output_tokens: int,
) -> Response:
    """Standard Response construction."""

# Model-specific conversions
def convert_tools_to_openai(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert tool schemas to OpenAI function format."""

def map_openai_stop_reason(finish_reason: str | None) -> str:
    """Map OpenAI finish_reason to internal stop_reason."""

def clean_schema_for_gemini(schema: dict[str, Any]) -> dict[str, Any]:
    """Remove unsupported schema keys for Gemini compatibility."""
```

**Benefit:** Reduced 126+ LOC duplication across Anthropic, OpenAI, Gemini providers.

**Usage Pattern:**
```python
from miu_core.providers.converters import (
    convert_messages_to_anthropic,
    build_response,
)

# In provider implementation
anthropic_messages = convert_messages_to_anthropic(messages)
response = build_response(
    response_id=response.id,
    content=response.content,
    stop_reason="end_turn",
    input_tokens=usage.input_tokens,
    output_tokens=usage.output_tokens,
)
```

### Session Storage Abstraction

The `miu_core.session` module provides a pluggable session storage interface:

**Base Class:**
```python
class SessionStorageBase(ABC):
    """Abstract interface for session persistence."""

    def __init__(self, session_id: str, base_dir: Path) -> None:
        """Initialize with session ID and storage directory."""

    @property
    @abstractmethod
    def session_file(self) -> Path:
        """Path to session storage file."""

    @abstractmethod
    def load(self) -> list[Message]:
        """Load messages from storage."""

    @abstractmethod
    def save(self, messages: list[Message]) -> None:
        """Persist messages to storage."""

    @abstractmethod
    def clear(self) -> None:
        """Delete session data."""

    def exists(self) -> bool:
        """Check if session exists (default implementation)."""
```

**JSONL Implementation:**
```python
class JSONLSessionStorage(SessionStorageBase):
    """JSONL-based session persistence.

    One message per line as JSON for:
    - Efficient appending (no re-write of entire file)
    - Streaming/progressive loading
    - Human-readable format for debugging
    """

    def __init__(
        self,
        session_id: str | None = None,
        base_dir: Path | None = None,
    ) -> None:
        """Auto-generate session ID if not provided."""
        sid = session_id or str(uuid.uuid4())[:8]
        bdir = base_dir or MiuPaths.get().sessions
        super().__init__(session_id=sid, base_dir=bdir)
```

**Pattern:** To add new storage backends (DB, S3, etc.), subclass `SessionStorageBase` and implement required methods.

### Token-Aware Memory Truncation

The `miu_core.memory.truncation` module provides model-specific token estimation and intelligent message truncation:

**Model-Specific Token Ratios:**
```python
TOKEN_RATIOS: dict[str, float] = {
    "claude": 3.5,   # Claude: ~3.5 chars per token
    "gpt": 4.0,      # GPT-4: ~4 chars per token
    "gemini": 3.8,   # Gemini: ~3.8 chars per token
    "default": 4.0,  # Conservative default
}

def get_token_ratio(model: str | None = None) -> float:
    """Detect model from prefix and return ratio."""

def estimate_tokens(message: Message, model: str | None = None) -> int:
    """Estimate tokens using model-specific ratio."""
```

**Truncation Strategies:**
```python
class TruncationStrategy(str, Enum):
    FIFO = "fifo"        # Remove oldest messages
    SLIDING = "sliding"  # Keep first + last N messages
    SUMMARIZE = "summarize"  # Future: LLM summarization

def truncate_fifo(
    messages: list[Message],
    max_tokens: int,
) -> tuple[list[Message], int]:
    """FIFO removal, keeping first message and recent ones."""

def truncate_sliding(
    messages: list[Message],
    max_tokens: int,
    keep_first: int = 1,
    keep_last: int = 10,
) -> tuple[list[Message], int]:
    """Keep first N and last M messages regardless of token count."""
```

**Usage:**
```python
from miu_core.memory.truncation import truncate_fifo

truncated, removed = truncate_fifo(messages, max_tokens=4096)
print(f"Removed {removed} tokens to fit context window")
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

## Testing Standards (Phase 03)

### Test Structure & Organization

**File Structure:**
```
packages/<package>/tests/
├── conftest.py           # Shared fixtures for package
├── __init__.py
├── test_<module>.py      # Tests for specific modules
└── test_<feature>.py     # Feature-specific tests

tests/integration/
├── conftest.py           # Cross-package shared fixtures
├── __init__.py
└── test_<integration>.py # Cross-package tests
```

**Class-Based Test Structure:**

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

### Test Fixtures (Phase 03)

**Shared Fixture Hierarchy:**

Package-level fixtures in `packages/<package>/tests/conftest.py` are reusable within that package.
Integration fixtures in `tests/integration/conftest.py` are shared across packages.

**Core Package Fixtures** (`packages/core/tests/conftest.py`):
- `mock_provider` - Basic mock LLM provider with configurable responses
- `mock_provider_with_tools` - Mock provider that returns tool use actions
- `sample_messages` - Pre-built conversation messages for testing
- `sample_tool_result` - Sample ToolResultContent for tool execution
- `memory` - ShortTermMemory instance for conversation history
- `memory_with_messages` - Memory pre-populated with sample messages
- `tool_registry` - Empty ToolRegistry ready for registration
- `tool_context` - Default ToolContext with working directory
- `temp_dir` - Temporary directory for file operations
- `tool_context_with_dir` - ToolContext with temp working directory
- `mock_tool_success` - Mock tool returning success
- `mock_tool_failure` - Mock tool returning failure

**Code Package Fixtures** (`packages/code/tests/conftest.py`):
- `temp_dir` - Temporary directory for file operations
- `ctx` - ToolContext with temp working directory
- `tool_registry` - Empty ToolRegistry for code tools
- `memory` - ShortTermMemory instance
- `mode_manager` - ModeManager with default mode
- `mode_manager_plan` - ModeManager in PLAN mode
- `usage_tracker` - UsageTracker with default limits
- `usage_tracker_100k` - UsageTracker with 100k token limit
- `sample_python_file` - Sample Python module with functions/classes
- `sample_config_file` - Sample JSON config file
- `nested_dir_structure` - Multi-level directory structure with files
- `mock_provider` - AsyncMock LLM provider
- `home_dir` - User home directory path
- `cwd` - Current working directory path

**Studio Package Fixtures** (`packages/studio/tests/conftest.py`):
- `temp_session_dir` - Temporary directory for session storage
- `session_manager` - SessionManager with temp directory
- `chat_service` - ChatService with test session manager
- `client` - FastAPI TestClient with injected session manager
- `client_with_chat` - TestClient with both session and chat services
- `session_id` - Create session and return its UUID
- `session_with_messages` - Session with pre-populated messages
- `valid_uuid` - Valid UUID format for testing (non-existent)
- `invalid_uuids` - List of invalid UUID formats

**Integration Fixtures** (`tests/integration/conftest.py`):
- `temp_dir` - Temporary directory for integration tests
- `tool_registry` - ToolRegistry with EchoTool for testing
- `memory` - ShortTermMemory instance
- `mock_provider` - MockProvider with configurable responses
- `agent_config` - Default AgentConfig for ReActAgent
- `react_agent` - Fully configured ReActAgent for testing

### Testing Conventions

- **Coverage Target:** ≥80% per package
- **Async Tests:** Use `@pytest.mark.asyncio` decorator
- **Mocking:** Use `unittest.mock` for external dependencies
- **Fixtures:** Define in `conftest.py` for reusability
- **Naming:** `test_<function_name>` or `test_<scenario>`
- **Isolation:** Each test independent; fixtures create fresh instances
- **Integration Tests:** Place cross-package tests in `tests/integration/`

### Running Tests

```bash
# All tests with coverage
uv run pytest --cov

# Specific package
uv run pytest packages/miu_core/

# Integration tests only
uv run pytest tests/integration/

# With verbose output
uv run pytest -v

# Watch mode (requires pytest-watch)
uv run pytest-watch
```

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

## Security Considerations (Phase 01 Hardening)

### Path Validation

Prevent directory traversal attacks using `Path.is_relative_to()`:

```python
from pathlib import Path

def validate_file_path(path: str, allowed_base: Path) -> Path:
    """Validate and sanitize file path."""
    resolved = Path(path).resolve()
    base = allowed_base.resolve()

    if not resolved.is_relative_to(base):
        raise ValueError(f"Path outside allowed directory: {path}")

    return resolved

# Example usage
def validate_session_path(session_id: str, session_dir: Path) -> Path:
    """Validate session ID is UUID format and path is safe."""
    # First validate UUID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise ValueError(f"Invalid session ID: {session_id}")

    # Then validate resolved path
    session_path = (session_dir / f"{session_id}.json").resolve()
    if not session_path.is_relative_to(session_dir.resolve()):
        raise ValueError("Invalid session path")

    return session_path
```

### Script Execution Security

Whitelist allowed script directories to prevent arbitrary script execution:

```python
from pathlib import Path

def validate_script_path(script: Path) -> bool:
    """Validate script is within allowed directories."""
    try:
        script = script.resolve()
        allowed_bases = [Path.cwd(), Path.home() / ".miu"]
        return any(script.is_relative_to(base) for base in allowed_bases)
    except (ValueError, OSError):
        return False
```

### Bash Tool Security (Phase 02)

Bash tool uses shell=True intentionally for user convenience (pipes, redirects, env vars, shell expansion).

**Security Model:** User is executing commands in their own environment.
- Path validation NOT applied (user may need full system access)
- For untrusted input: use subprocess with shell=False instead
- Document security implications in docstrings

**Implementation:** `miu_code.tools.bash.BashTool`
```python
"""Bash command execution tool.

Security Note:
    Uses shell=True (via create_subprocess_shell) for user convenience -
    enables pipes, redirects, env vars, and shell expansion.
    This is intentional: user is executing commands in their own environment.
    Path validation is NOT applied as user may need full system access.

    For untrusted input, use subprocess with shell=False instead.
"""
```

### CORS & Rate Limiting (Phase 01)

Restrict CORS origins and implement rate limiting:

```python
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# CORS - never use ["*"] in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Config-driven, defaults to localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting endpoints
@router.post("/invoke")
@limiter.limit("10/minute")
async def invoke(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """Endpoint limited to 10 requests per minute."""
    pass
```

### Input Size Validation

Prevent DoS attacks via large messages:

```python
# Constants
MAX_MESSAGE_SIZE = 64 * 1024  # 64KB max message
MAX_JSON_SIZE = 10 * 1024 * 1024  # 10MB max JSON response

# Validation in WebSocket handler
if len(message) > MAX_MESSAGE_SIZE:
    raise ValueError("Message too large (max 64KB)")
```

### UUID Format Validation

Validate session IDs prevent path traversal:

```python
import uuid

def validate_session_id(session_id: str) -> None:
    """Validate session ID is a valid UUID."""
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
```

### Security Headers

Add CSP and Cache-Control headers for static content:

```python
@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    response = FileResponse(static_dir / "index.html")
    # Prevent XSS, unsafe inline scripts
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' ws: wss:; "
    )
    return response
```

### Environment Variables

Load all secrets from environment variables with proper defaults:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Load from environment with MIU_ prefix."""

    # CORS origins - configurable, defaults to localhost
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Set via MIU_CORS_ORIGINS env var"
    )

# Good - use environment variables for secrets
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

# Bad - never hardcode credentials
api_key = "sk-1234567890"  # Don't do this!
```

## CI/CD Security Scanning (Phase 04)

Automated security scanning is integrated into the CI pipeline via GitHub Actions:

### Bandit - Static Security Analysis

**Purpose:** Detects common security issues in Python code
- Hardcoded credentials
- Insecure shell operations
- SQL injection vulnerabilities
- Insecure deserialization

**Configuration:**
```yaml
# .github/workflows/ci.yml - security job
- name: Run Bandit security scan
  run: |
    bandit -r packages/ -ll -x "*/tests/*" || true
```

**Flags:**
- `-r packages/` - Recursive scan of packages
- `-ll` - Report only medium/high severity (filter low-confidence issues)
- `-x "*/tests/*"` - Exclude test files from scanning

**Output:** Non-blocking (|| true), issues reported but don't fail CI.

### pip-audit - Dependency Vulnerability Scanning

**Purpose:** Detects known security vulnerabilities in dependencies
- CVE database matching
- Version conflict detection
- Transitive dependency scanning

**Configuration:**
```yaml
- name: Run pip-audit for vulnerabilities
  run: |
    uv export --no-dev > requirements.txt
    pip-audit -r requirements.txt || true
```

**Process:**
1. Export production dependencies (no dev/test packages)
2. Scan against known vulnerability database
3. Report but don't fail CI

**Output:** Non-blocking, informational alerts for review.

### Security Job Dependencies

The security scan is gated by test and type-check jobs:
```yaml
jobs:
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    # Runs independently but must pass for ci-success
    steps: [bandit, pip-audit]

  ci-success:
    needs: [lint, typecheck, test, security]
    # Enforces all four checks must pass
```

### Integration with Development

**Local Security Checks (Optional):**
```bash
# Install security tools
pip install bandit pip-audit

# Run Bandit locally
bandit -r packages/

# Run pip-audit
pip-audit -r <(uv export --no-dev)
```

**Workflow:**
1. Developers push code to PR branch
2. CI automatically runs security scans
3. Developers review security reports in workflow
4. Address issues before merging to main

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
**Last Review:** 2026-01-01
**Latest Additions:**
- Phase 04: DRY Refactoring - Provider Converters (126 LOC dedup)
- Phase 04: Session Storage Abstraction (pluggable persistence)
- Phase 04: Token-Aware Memory Truncation (model-specific ratios)
- Phase 04: CI Security Scanning (Bandit + pip-audit)
- Phase 03: Test Infrastructure (fixtures, conftest, integration tests)
- Phase 03: py.typed markers for type-checking exports
- Phase 03: 15 ReAct agent tests and cross-package integration tests
