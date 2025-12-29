# Miumono Codebase Summary

**Project:** AI Agent Framework Monorepo
**Version:** 0.1.0
**Status:** Phase 1A - Complete (MVP Tier 1 Delivered)
**Updated:** 2025-12-29

## Overview

Miumono is a Python-based AI agent framework designed for building AI-powered coding assistants. Built as a monorepo using UV workspace management, it provides a modular architecture separating core framework functionality from CLI/agent implementations.

## Project Structure

```
miumono/
├── packages/
│   ├── miu_core/           # Core framework library
│   └── miu_code/           # AI coding agent with CLI
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
