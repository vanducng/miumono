# miu-mono Codebase Summary

**Project:** AI Agent Framework Monorepo
**Version:** 0.1.0
**Status:** Tier 4 - Type Safety & Protocol Hardening (Complete)
**Updated:** 2025-12-30
**PyPI Status:** All 5 packages published at version 0.1.0

## Overview

miu-mono is a Python-based AI agent framework monorepo supporting multiple tiers: core framework (Tier 1), coding agent CLI (Tier 2), orchestration layer (Tier 3), and web server UI (Tier 4). Built with UV workspace management, provides modular architecture from framework to web service. All packages published to PyPI as of 2025-12-30.

## Project Structure

```
miu-mono/
├── packages/
│   ├── miu_core/           # Core framework library (0.1.0 on PyPI)
│   ├── miu_code/           # AI coding agent with CLI (0.1.0 on PyPI)
│   ├── miu_studio/         # Web server and UI (0.1.0 on PyPI)
│   ├── miu_examples/       # Example applications (0.1.0 on PyPI)
│   └── miu_mono/           # Meta-package (0.1.0 on PyPI)
├── .claude/                # Claude Code configuration & workflows
├── .secrets/               # Secrets management (git-ignored)
├── .venv/                  # Python virtual environment
├── pyproject.toml          # Root workspace configuration
├── repomix-output.xml      # Codebase summary artifact
├── README.md               # Quick start guide
└── CLAUDE.md               # Development guidelines
```

## Packages

### miu-core

**Purpose:** Core framework library providing foundational abstractions for AI agents.

**Location:** `/packages/miu_core/`

**Dependencies:**
- pydantic>=2.0 (data validation, serialization)
- httpx>=0.27 (async HTTP client)
- aiofiles>=23.0 (async file operations)
- packaging>=24.0 (version management)

**Optional Dependencies:**
- anthropic>=0.40 (Anthropic Claude provider)
- openai>=1.50 (OpenAI provider)
- google-genai>=0.8 (Google Gemini provider)
- mcp>=1.0 (Model Context Protocol)

**Key Modules:**

| Module | Purpose |
|--------|---------|
| `miu_core.agents` | Agent framework base classes |
| `miu_core.models` | Data models for agents, tools, messages |
| `miu_core.providers` | LLM provider integrations (Anthropic, OpenAI, Google) |
| `miu_core.tools` | Tool registry and base tool abstractions |
| `miu_core.patterns` | Multi-agent patterns (Orchestrator, Pipeline, Router) |
| `miu_core.tracing` | OpenTelemetry integration with no-op fallback |
| `miu_core.usage` | Token usage tracking and statistics (Phase 2) |
| `miu_core.modes` | Agent mode management (normal, plan, ask) (Phase 2) |
| `miu_core.version` | Version management |

**Example Usage:**

```python
from miu_core.providers import AnthropicProvider
from miu_core.agents import ReActAgent

provider = AnthropicProvider()
agent = ReActAgent(provider=provider)
response = await agent.run("Hello!")
```

**Phase 2 Modules (New):**

**miu_core.usage** - Token usage tracking:
```python
from miu_core import UsageTracker, UsageStats

# Track token usage across a session
tracker = UsageTracker(context_limit=200_000)
tracker.add_usage(input_tokens=150, output_tokens=50)

# Get statistics
print(tracker.total_tokens)  # 200
print(tracker.usage_percent)  # 0.1
print(tracker.format_usage())  # "0% of 200k tokens"

# Stats object
stats = tracker.stats
print(stats.input_tokens, stats.output_tokens)
```

**miu_core.modes** - Agent mode management:
```python
from miu_core import AgentMode, ModeManager

# Manage agent operation modes
mode_mgr = ModeManager(initial=AgentMode.NORMAL)

# Cycle through modes: NORMAL -> PLAN -> ASK -> NORMAL
next_mode = mode_mgr.cycle()  # Returns AgentMode.PLAN

# Get current mode info
print(mode_mgr.mode)  # AgentMode.PLAN
print(mode_mgr.label)  # "plan mode"
print(mode_mgr.format_status())  # "plan mode (shift+tab to cycle)"

# Listen to mode changes
def on_mode_change(mode: AgentMode):
    print(f"Mode changed to: {mode.value}")

mode_mgr.on_change(on_mode_change)
```

### miu-code

**Purpose:** AI coding agent with CLI interface for file/shell operations.

**Location:** `/packages/miu_code/`

**Dependencies:**
- miu-core[anthropic] (core framework with Anthropic)
- asyncclick>=8.1 (async CLI framework)
- rich>=13.0 (terminal output formatting)
- prompt-toolkit>=3.0 (interactive REPL)

**Key Modules:**

| Module | Purpose |
|--------|---------|
| `miu_code.agent` | Coding-specific agent implementation |
| `miu_code.cli` | Command-line interface & entry point |
| `miu_code.tools` | Coding tools (read, write, edit, bash, glob, grep) |
| `miu_code.session` | Session management & persistence |
| `miu_code.tui` | TUI interface with Textual widgets (Phase 3) |
| `miu_code.tui.widgets` | Reusable TUI components (StatusBar, WelcomeBanner, etc.) |

**CLI Entry Points:**
- `miu` - Main CLI command
- `miu-code` - Alias for `miu`

**Features:**
- One-shot queries: `miu -q "read package.json"` or `miu --query "read package.json"`
- Interactive REPL mode: `miu` (launch interactive mode)
- Interactive TUI mode: `miu code` (graphical interface)
- File operations: read, write, edit
- Shell command execution
- File pattern matching (glob)
- Content search (grep)
- Session persistence

**Example Usage:**

```bash
# One-shot query
miu -q "read package.json"
miu --query "read package.json"

# Interactive REPL mode
miu

# Interactive TUI mode (Phase 4 - Full Textual app)
miu code

# TUI with specific model
miu code --model "anthropic:claude-opus-4-20250805"
```

**TUI Application (Phase 4 - Full Integration):**

**Interactive Controls:**
- `shift+tab` - Cycle through modes (NORMAL → PLAN → ASK → NORMAL)
- `ctrl+n` - Start new session (resets agent, clears history)
- `ctrl+l` - Clear chat log
- `ctrl+c` - Quit application

**Keyboard Bindings:**
- Enter - Submit query/command
- `ctrl+c` - Exit application

**Status Display (StatusBar):**
- **Left:** Current mode indicator
- **Center:** Working directory path (abbreviated with ~)
- **Right:** Token usage (input/output counts, total percentage)

**Features:**
- Real-time streaming responses
- Tool execution display during agent reasoning
- Token usage tracking (accumulated across session)
- Session persistence (can create multiple sessions)

**TUI Widgets (Phase 3 - NEW):**

Location: `miu_code/tui/widgets/`

| Widget | Purpose |
|--------|---------|
| `StatusBar` | Footer status bar showing mode, path, token usage |
| `WelcomeBanner` | Animated welcome banner with metadata (version, model, MCP) |
| `ChatLog` | Chat message display with scrolling |
| `MessageInput` | Text input field for user queries |
| `LoadingSpinner` | Animated loading spinner |

StatusBar features:
```python
from miu_code.tui.widgets import StatusBar
from miu_core.modes import ModeManager
from miu_core.usage import UsageTracker

# Create status bar
bar = StatusBar(
    mode_manager=ModeManager(),
    usage_tracker=UsageTracker(),
    working_dir="/home/user/project"
)

# Update on mode/usage changes
bar.update_usage(input_tokens=100, output_tokens=50)
bar.update_path("/new/path")

# Access mode manager for cycling
mode_manager = bar.mode_manager
```

WelcomeBanner features:
```python
from miu_code.tui.widgets import WelcomeBanner

banner = WelcomeBanner(
    version="0.2.0",
    model="claude-opus-4-20250805",
    mcp_count=2,
    working_dir="/home/user/miu-mono",
    compact=True  # Use compact logo
)
```

**Test Coverage (Phase 3):**
- 40 widget tests covering StatusBar, WelcomeBanner, and integrations
- Mode cycling and usage tracking
- Path formatting (home directory abbreviation)
- Animation state management
- Widget initialization edge cases
- Location: `tests/test_tui_widgets.py`

### miu-studio

**Purpose:** Web server providing FastAPI-based REST API and UI for miu AI agent framework.

**Location:** `/packages/miu_studio/`

**Dependencies:**
- miu-core[anthropic] (core framework with Anthropic)
- fastapi>=0.115 (async web framework)
- uvicorn[standard]>=0.32 (ASGI server)
- pydantic-settings>=2.6 (configuration management)
- websockets>=13.0 (WebSocket support)

**Key Modules:**

| Module | Purpose |
|--------|---------|
| `miu_studio.main` | FastAPI application factory & setup |
| `miu_studio.core.config` | Settings management via Pydantic |
| `miu_studio.api.routes` | REST API endpoints |
| `miu_studio.services` | Business logic services |
| `miu_studio.static` | Static assets for web UI |

**Features:**
- REST API endpoints for agent operations
- Health check endpoints (`/api/v1/health`, `/api/v1/ready`)
- CORS middleware for web client support
- Static file serving for UI
- Session management (directory: `.miu/sessions`)
- Configurable via environment variables (`MIU_*` prefix)
- Uvicorn ASGI server with standard features

**Configuration (Environment Variables):**
```bash
# Server
MIU_HOST=0.0.0.0
MIU_PORT=8000
MIU_DEBUG=false

# CORS
MIU_CORS_ORIGINS=["*"]

# Agent
MIU_DEFAULT_MODEL=claude-sonnet-4-20250514
MIU_DEFAULT_PROVIDER=anthropic
MIU_MAX_TOKENS=4096
MIU_MAX_ITERATIONS=10

# Sessions
MIU_SESSION_DIR=.miu/sessions
MIU_SESSION_TIMEOUT=3600

# Logging
MIU_LOG_LEVEL=INFO
```

**API Endpoints:**

*Health & Status:*
```
GET  /api/v1/health   - Server health status
GET  /api/v1/ready    - Server readiness probe
```

*Sessions:*
```
GET    /api/v1/sessions/              - List all sessions (returns SessionSummary[])
POST   /api/v1/sessions/              - Create new session (accepts CreateSessionRequest)
GET    /api/v1/sessions/{id}          - Get session by ID (returns Session)
DELETE /api/v1/sessions/{id}          - Delete session (returns {deleted: string})
```

**Session Management (NEW - Phase 4B):**

*Models:*
- `SessionMessage` - Message with role (user/assistant/system), content, timestamp
- `Session` - Full session: id, name, model, system_prompt, messages, created_at, updated_at
- `SessionSummary` - Session listing: id, name, created_at, updated_at, message_count
- `CreateSessionRequest` - Create request: name?, model?, system_prompt?

*SessionManager Service:*
- Location: `miu_studio.services.session_manager`
- Persistence: File-based (JSON) in `MIU_SESSION_DIR`
- UUID validation prevents path traversal attacks
- Async file I/O via aiofiles
- List, create, get, update, delete operations
- Automatic sorting by updated_at (newest first)
- Error handling: JSONDecodeError, ValueError recovery

*Security:*
- UUID format validation on all session_id parameters
- Path traversal prevention via strict validation
- HTTP 400 for invalid format, 404 for not found
- File-level isolation with UUID filenames

**Entry Point:**
```bash
miu-studio  # Start web server (CLI command)
```

**Example Usage:**

```python
from miu_studio.main import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/vanducng/miu-mono.git
cd miu-mono

# Install all dependencies (uses uv workspace)
uv sync
```

### Development Commands

**Linting (Ruff):**
```bash
# Check code style
uv run ruff check .

# Auto-format code
uv run ruff format .
```

**Type Checking (MyPy):**
```bash
# Type check all packages
uv run mypy packages/
```

**Testing (Pytest):**
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest packages/miu_core/tests/test_core_tools.py
```

**Combined:**
```bash
# Full development cycle
uv sync && uv run ruff check . && uv run mypy packages/ && uv run pytest
```

### Code Quality Standards

**Configuration:** `pyproject.toml`

**Ruff (Linting & Formatting):**
- Line length: 100 characters
- Target Python version: 3.11
- Rules: E (pycodestyle errors), F (Pyflakes), W (warnings), I (isort), UP (upgrades), B (flake8-bugbear), RUF (Ruff-specific)
- Excluded: E501 (line too long - handled by formatter)
- Quote style: double quotes
- Indent: 4 spaces

**MyPy (Type Checking):**
- Python version: 3.11
- Strict mode: enabled
- Warnings: unused ignores, return_any
- Known modules: miu_core, miu_code
- Exclude: tests/

**Pytest (Testing):**
- AsyncIO mode: auto
- Test paths: packages/miu_core/tests, packages/miu_code/tests
- Python path: packages/miu_core, packages/miu_code
- Verbosity: -v (verbose)
- Traceback format: short

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Python | CPython | 3.11+ |
| Package Manager | UV | Latest |
| Async Runtime | asyncio | Built-in |
| Data Validation | Pydantic | 2.0+ |
| HTTP Client | httpx | 0.27+ |
| Web Framework | FastAPI | 0.115+ |
| ASGI Server | Uvicorn | 0.32+ |
| WebSocket | websockets | 13.0+ |
| Settings | Pydantic Settings | 2.6+ |
| LLM Providers | Anthropic/OpenAI/Google | Multi-provider |
| CLI Framework | asyncclick | 8.1+ |
| Terminal UI | rich | 13.0+ |
| Testing | pytest | 8.0+ |
| Linting | ruff | 0.8+ |
| Type Checking | mypy | 1.13+ |

## Dependencies Overview

**Core Framework Dependencies:**
- **pydantic:** Runtime type checking and data validation
- **httpx:** Async HTTP operations for provider APIs
- **aiofiles:** Non-blocking file I/O
- **packaging:** Version parsing and comparison

**CLI Dependencies:**
- **asyncclick:** Async-first CLI framework
- **rich:** Terminal output formatting and styling
- **prompt-toolkit:** Interactive REPL with features like history, autocomplete

**Provider Dependencies (Optional):**
- **anthropic:** Anthropic Claude API integration
- **openai:** OpenAI API integration
- **google-genai:** Google Gemini API integration
- **mcp:** Model Context Protocol for tool extensions

**Development Dependencies:**
- **pytest:** Test framework
- **pytest-asyncio:** Async test support
- **pytest-cov:** Code coverage reporting
- **ruff:** Linting and formatting
- **mypy:** Static type checking

## Build System

**Build Backend:** hatchling
**Packages to Include:** miu_core, miu_code
**Python Version:** >=3.11

## Key Files

| File | Purpose |
|------|---------|
| `/pyproject.toml` | Root workspace configuration with all tool settings |
| `/packages/miu_core/pyproject.toml` | miu-core package metadata |
| `/packages/miu_code/pyproject.toml` | miu-code package metadata |
| `/packages/miu_studio/pyproject.toml` | miu-studio package metadata |
| `/packages/miu_studio/miu_studio/main.py` | FastAPI application factory |
| `/packages/miu_studio/miu_studio/core/config.py` | Settings configuration |
| `/packages/miu_studio/miu_studio/api/routes/health.py` | Health check endpoints |
| `/packages/miu_studio/miu_studio/api/routes/sessions.py` | Session management endpoints |
| `/packages/miu_studio/miu_studio/services/session_manager.py` | SessionManager service |
| `/packages/miu_studio/miu_studio/models/api.py` | Pydantic models for API |
| `/packages/miu_studio/tests/test_sessions.py` | Session tests (11 test cases) |
| `/README.md` | Quick start and overview |
| `/CLAUDE.md` | Development guidelines and workflows |
| `/repomix-output.xml` | Full codebase artifact (generated) |

## Development Guidelines

**Python Version:** 3.11+
**Code Style:** Follow Ruff configuration in pyproject.toml
**Type Safety:** Strict MyPy mode required for all code
**Testing:** All code must be tested with pytest
**Async:** Use asyncio patterns consistently

## Quick Reference Commands

```bash
# Install workspace
uv sync

# Run all checks
uv run ruff check . && uv run mypy packages/ && uv run pytest

# Format code
uv run ruff format .

# Test specific package
uv run pytest packages/miu_core/tests

# Run CLI
miu -q "your query"          # One-shot query
miu                          # Interactive REPL mode
miu code                     # Interactive TUI mode
miu --model openai:gpt-4o -q "query"  # With specific provider
```

## Session Management API (Tier 4 Phase 4B)

**Status:** Phase 4B Complete

### Routes (`/api/v1/sessions`)

1. **List Sessions** - `GET /api/v1/sessions/`
   - Returns: `list[SessionSummary]`
   - No parameters
   - Sorted by updated_at (newest first)

2. **Create Session** - `POST /api/v1/sessions/`
   - Body: `CreateSessionRequest` (optional)
   - Returns: `Session` with new ID (UUID)
   - Defaults: model from config, no name/system_prompt

3. **Get Session** - `GET /api/v1/sessions/{session_id}`
   - Param: session_id (must be valid UUID)
   - Returns: `Session` (404 if not found)
   - Errors: 400 (invalid format), 404 (not found)

4. **Delete Session** - `DELETE /api/v1/sessions/{session_id}`
   - Param: session_id (must be valid UUID)
   - Returns: `{deleted: string}` (session ID)
   - Errors: 400 (invalid format), 404 (not found)

### Test Coverage (11 tests)

- Session CRUD operations (create, read, update, delete)
- List with empty sessions
- List with multiple sessions (sorted correctly)
- Invalid session ID format rejection
- Non-existent session handling
- Message persistence
- Optional fields handling
- Security: path traversal prevention

### Implementation Details

**Persistence:** File-based JSON in `.miu/sessions/` directory
**File Format:** `{uuid}.json` with Session model serialization
**Async I/O:** Uses aiofiles for non-blocking operations
**Validation:** Pydantic model validation + UUID format checks
**Timestamps:** ISO 8601 via datetime.utcnow()

## Type Safety & Tracing Improvements (Tier 4 - Type Fixes)

**Status:** Type system hardening and protocol improvements

### Tracing System Type Protocols

Location: `packages/miu_core/miu_core/tracing/`

**Protocols Added:**
- `Span` (Protocol): Defines contract for span objects with methods: `set_attribute()`, `set_status()`, `record_exception()`, `end()`, context manager support
- `Tracer` (Protocol): Defines contract for tracer objects with methods: `start_as_current_span()`, `start_span()`

**Implementation:**
- `NoOpSpan`: Implements Span protocol with no-op behavior (fallback when OpenTelemetry unavailable)
- `NoOpTracer`: Implements Tracer protocol, returns NoOpSpan instances

**Usage Pattern:**
```python
from miu_core.tracing import get_tracer

tracer = get_tracer("miu.agent")
with tracer.start_as_current_span("operation.name") as span:
    span.set_attribute("key", "value")
    # Do work
    span.set_attribute("result", "success")
```

### Agent Configuration Type Improvements

**File:** `packages/miu_core/miu_core/agents/base.py`

**Changes:**
- Added `name: str = "agent"` field to `AgentConfig` (enables agent identification in tracing)
- AgentConfig now fully captures agent identity and constraints

### Provider Tracer Typing

**Files:**
- `packages/miu_core/miu_core/agents/react.py` - ReActAgent._tracer typed as `Tracer` protocol
- `packages/miu_core/miu_core/providers/anthropic.py` - AnthropicProvider._tracer typed as `Tracer` protocol

**Pattern:** All providers and agents consistently declare tracer field with explicit Tracer protocol type for type safety

### Type Ignore Fixes

**Files:**
- `packages/miu_core/miu_core/providers/google.py` - `type: ignore[assignment]` on tools conversion (Google API type constraints)
- `packages/miu_mono/miu_mono/cli.py` - Version import from miu_mono module

**Reasoning:** Justified type ignores for third-party API constraints while maintaining strict mypy elsewhere

### Example Package Typing

**File:** `packages/miu_examples/miu_examples/tool_usage.py`

**Type Improvements:**
- Fixed AST typing for calculator tool (operator module type safety)
- Proper type annotations for eval-based expression handling

### TUI Type Updates

**File:** `packages/miu_code/miu_code/tui/app.py`

**Changes:**
- `BindingType` imported from `textual.binding` (explicit type for BINDINGS class variable)
- Textual UI binding declarations now type-safe: `BINDINGS: ClassVar[list[BindingType]]`

### MCP Client API Updates

**File:** `packages/miu_examples/miu_examples/mcp_client.py`

**API Improvements:**
- `client.get_tools()` - Returns typed list of tool dictionaries
- `client.call_tool(name, params)` - Async tool invocation with proper type hints
- MCPClient async context manager protocol maintained

## Multi-Agent Patterns (Phase 4H)

**Location:** `packages/miu_core/miu_core/patterns/`

Three multi-agent coordination patterns implemented:

### Orchestrator Pattern

Coordinates multiple agents with task dependencies using DAG-based execution.

```python
from miu_core.patterns import Orchestrator

orchestrator = Orchestrator()
orchestrator.add_agent("researcher", research_agent)
orchestrator.add_agent("writer", writer_agent)

orchestrator.add_task("research", "researcher", "Research AI agents")
orchestrator.add_task(
    "write", "writer",
    lambda ctx: f"Write about: {ctx['research'].response.get_text()}",
    depends_on=["research"],
)

results = await orchestrator.run()
```

### Pipeline Pattern

Sequential agent chain where output feeds to next stage.

```python
from miu_core.patterns import Pipeline

pipeline = Pipeline()
pipeline.add_stage("research", research_agent)
pipeline.add_stage(
    "summarize", summarizer_agent,
    transform=lambda q, r: f"Summarize: {r.get_text()}"
)

result = await pipeline.run("Research quantum computing")
```

### Router Pattern

Routes requests to appropriate agents based on keywords, patterns, or conditions.

```python
from miu_core.patterns import Router

router = Router()
router.add_route("code", code_agent, keywords=["python", "debug"])
router.add_route("writing", write_agent, keywords=["write", "article"])
router.add_route("general", general_agent, condition=lambda q: True, priority=-1)

result = await router.route("Help me debug Python code")
```

### miu-examples Package

**Location:** `packages/miu_examples/`

Example applications demonstrating miu framework usage:

| Example | Purpose |
|---------|---------|
| `simple_agent.py` | Basic agent usage |
| `multi_provider.py` | Provider switching |
| `tool_usage.py` | Custom tools with safe eval |
| `mcp_client.py` | MCP integration |
| `rag_agent.py` | RAG with vector DB |
| `multi_agent.py` | All three patterns demo |

### miu-mono Glue Package

**Location:** `packages/miu_mono/`

Meta-package providing unified CLI dispatcher with optional dependencies. Published to PyPI as `miu-mono` v0.1.0.

```bash
miu              # Run miu-code CLI (default)
miu serve        # Run miu-studio web server
miu code         # Run miu-code CLI
miu tui          # Run miu-code TUI
miu --version    # Show version
```

**Installation:**
```bash
# Full installation with all extras
pip install "miu-mono[all]"

# Or individual packages
pip install miu-core miu-code miu-studio
```

## Documentation Files

- `project-overview-pdr.md` - Project requirements and architecture
- `code-standards.md` - Detailed code standards and patterns
- `system-architecture.md` - System design and component interactions
- `codebase-summary.md` - This file - complete codebase overview
- `deployment-guide.md` - Deployment and release procedures
- `project-roadmap.md` - Feature roadmap and milestones

## TUI Implementation (Phase 3-4)

**Phase 3 Status:** Complete - StatusBar and WelcomeBanner widgets implemented and tested

**Phase 4 TUI Integration Status:** Complete - Full TUI app integrated with agents, modes, and usage tracking

**Phase 3 Components:**
- StatusBar widget with mode/path/usage display
- WelcomeBanner with animated intro and metadata
- Integration with ModeManager and UsageTracker
- 40 comprehensive widget tests

**Phase 4 Integration Features:**
- Full MiuCodeApp with Textual-based interface
- Real-time streaming event handling (TextDelta, ToolExecuting, ToolResult)
- Token usage tracking from streaming responses
- Mode cycling with shift+tab (normal → plan → ask)
- Dynamic StatusBar showing current mode | working directory | token usage
- Session management (new session via ctrl+n)
- Chat clearing (ctrl+l)
- MessageStopEvent now includes usage field for token propagation

**Phase 3 Test Coverage:**
- StatusBar: 11 tests (instantiation, mode cycling, usage tracking, path formatting)
- WelcomeBanner: 10 tests (metadata, path formatting, animation, logo parsing)
- Integration tests: 12 tests (mode callbacks, usage accumulation)
- Render/edge case tests: 7 tests (animation boundaries, widget initialization)

**Phase 4 Key Files:**
- `packages/miu_code/miu_code/tui/app.py` - NEW: MiuCodeApp main application with streaming integration
- `packages/miu_code/miu_code/tui/app.tcss` - NEW: Teal/cyan brand styling
- `packages/miu_core/miu_core/models/messages.py` - MODIFIED: MessageStopEvent.usage field added
- `packages/miu_core/miu_core/providers/anthropic.py` - MODIFIED: Usage propagation in streaming

**Phase 3 Files:**
- `packages/miu_code/miu_code/tui/widgets/status.py`
- `packages/miu_code/miu_code/tui/widgets/banner.py`
- `packages/miu_code/miu_code/tui/widgets/__init__.py`
- `packages/miu_code/tests/test_tui_widgets.py`

---

**Last Updated:** 2025-12-30
**Maintained By:** Development Team
**Current Status:** Phase 3 Complete - TUI Widgets fully implemented and tested
**PyPI Status:** All 5 packages published at version 0.1.0
**Repository:** https://github.com/vanducng/miu-mono
