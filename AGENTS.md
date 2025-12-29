# AGENTS.md

This file provides instructions for AI coding agents working in this repository.

## Project Overview

miu is a Python AI agent framework monorepo with multiple packages:

| Package | Description |
|---------|-------------|
| `miu-core` | Core framework library (agents, tools, providers, tracing) |
| `miu-code` | CLI/TUI coding agent with filesystem access |
| `miu-examples` | Example applications and usage patterns |
| `miu-studio` | Web server + UI for browser-based interaction |
| `miu` | Meta-package bundling all components |

## Development Setup

```bash
# Clone and install
git clone https://github.com/vanducng/miumono.git
cd miumono
uv sync

# Verify setup
uv run pytest
uv run ruff check .
uv run mypy packages/
```

## Code Style

- **Python:** 3.11+ required
- **Type hints:** Required on all public APIs
- **Docstrings:** Google style
- **Line length:** 100 characters
- **Formatter:** Ruff
- **Linter:** Ruff + mypy (strict)

## Project Structure

```
miumono/
├── packages/
│   ├── miu_core/       # Core framework
│   ├── miu_code/       # CLI agent
│   ├── miu_examples/   # Examples
│   ├── miu_studio/     # Web UI
│   └── miu/            # Meta-package
├── docs/               # Documentation
├── scripts/            # Build/release scripts
└── pyproject.toml      # Workspace root
```

Each package follows:
```
packages/<name>/
├── pyproject.toml      # Package config
├── <name>/             # Source code
│   ├── __init__.py
│   └── ...
└── tests/              # Package tests
```

## Common Tasks

```bash
# Run all tests
uv run pytest

# Run tests for specific package
uv run pytest packages/miu_core

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy packages/

# Build docs locally
uv run mkdocs serve
```

## Testing Guidelines

1. Write tests in `packages/<name>/tests/`
2. Use pytest fixtures for setup
3. Mock external API calls (Anthropic, Google, OpenAI)
4. Aim for >80% coverage on new code

## Making Changes

1. Create feature branch from `main`
2. Write tests first (TDD encouraged)
3. Implement feature
4. Ensure all checks pass:
   ```bash
   uv run ruff check .
   uv run mypy packages/
   uv run pytest
   ```
5. Create PR with descriptive title

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Root workspace configuration |
| `packages/*/pyproject.toml` | Individual package configs |
| `.github/workflows/ci.yml` | CI pipeline (lint, type, test) |
| `.github/workflows/release.yml` | PyPI publishing |
| `mkdocs.yml` | Documentation site config |

## Architecture Notes

### Provider System
- Abstract `LLMProvider` base class
- Implementations: `AnthropicProvider`, `GoogleProvider`, `OpenAIProvider`
- Factory pattern via `create_provider()`

### Agent System
- `BaseAgent` → `ReActAgent` hierarchy
- Tool execution via `ToolManager`
- Hooks system for extensibility

### Tracing
- OpenTelemetry integration via `miu_core.tracing`
- NoOp fallback when OTEL not configured
- Spans for agent iterations, tool calls, LLM requests

## Dependencies

Internal dependencies flow: `miu-core` ← `miu-code`, `miu-examples`, `miu-studio` ← `miu`

External key deps:
- `anthropic`, `google-genai`, `openai` - LLM providers
- `textual` - TUI framework
- `fastapi` - Web server
- `pydantic` - Data validation
