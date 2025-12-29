# Miumono Codebase Summary

**Project:** AI Agent Framework Monorepo
**Version:** 0.1.0
**Status:** Tier 4 Phase 4A - Studio Web Server (Delivered)
**Updated:** 2025-12-29

## Overview

Miumono is a Python-based AI agent framework monorepo supporting multiple tiers: core framework (Tier 1), coding agent CLI (Tier 2), orchestration layer (Tier 3), and web server UI (Tier 4). Built with UV workspace management, provides modular architecture from framework to web service.

## Project Structure

```
miumono/
├── packages/
│   ├── miu_core/           # Core framework library
│   ├── miu_code/           # AI coding agent with CLI
│   └── miu_studio/         # Web server and UI (NEW - Tier 4)
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
| `miu_core.version` | Version management |

**Example Usage:**

```python
from miu_core.providers import AnthropicProvider
from miu_core.agents import ReActAgent

provider = AnthropicProvider()
agent = ReActAgent(provider=provider)
response = await agent.run("Hello!")
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

**CLI Entry Points:**
- `miu` - Main CLI command
- `miu-code` - Alias for `miu`

**Features:**
- One-shot queries: `miu "read package.json"`
- Interactive REPL mode: `miu`
- File operations: read, write, edit
- Shell command execution
- File pattern matching (glob)
- Content search (grep)
- Session persistence

**Example Usage:**

```bash
# One-shot query
miu "read package.json"

# Interactive mode
miu
```

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
```
GET  /api/v1/health   - Server health status
GET  /api/v1/ready    - Server readiness probe
```

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
git clone https://github.com/vanducng/miumono.git
cd miumono

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
miu "your query"
miu  # interactive mode
```

## Documentation Files

- `project-overview-pdr.md` - Project requirements and architecture
- `code-standards.md` - Detailed code standards and patterns
- `system-architecture.md` - System design and component interactions
- `deployment-guide.md` - Deployment and release procedures
- `project-roadmap.md` - Feature roadmap and milestones

---

**Last Updated:** 2025-12-29
**Maintained By:** Development Team
