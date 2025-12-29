# Miumono

[![CI](https://github.com/vanducng/miumono/actions/workflows/ci.yml/badge.svg)](https://github.com/vanducng/miumono/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/miu-code)](https://pypi.org/project/miu-code/)
[![Python](https://img.shields.io/pypi/pyversions/miu-code)](https://pypi.org/project/miu-code/)
[![License](https://img.shields.io/github/license/vanducng/miumono)](LICENSE)

AI Agent Framework Monorepo - Build and run AI coding agents with multiple LLM providers.

## Installation

### Quick Install (Recommended)

**Unix/macOS:**
```bash
curl -LsSf https://raw.githubusercontent.com/vanducng/miumono/main/scripts/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/vanducng/miumono/main/scripts/install.ps1 | iex
```

### Using uv

```bash
# Install as a tool (recommended)
uv tool install miu-code

# Or run directly without installing
uvx miu-code "read README.md"
```

### Using pip

```bash
# CLI agent
pip install miu-code

# Full installation with all extras
pip install "miu-mono[all]"
```

## Quick Start

```bash
# Run a query
miu "explain this codebase"

# Interactive mode
miu

# With specific provider
miu --provider google "summarize README.md"
```

## Packages

| Package | PyPI | Description |
|---------|------|-------------|
| [miu-core](packages/miu_core/) | `pip install miu-core` | Core framework library |
| [miu-code](packages/miu_code/) | `pip install miu-code` | AI coding agent with CLI/TUI |
| [miu-examples](packages/miu_examples/) | `pip install miu-examples` | Example applications |
| [miu-studio](packages/miu_studio/) | `pip install miu-studio` | Web server and UI |
| [miu-mono](packages/miu_mono/) | `pip install miu-mono` | Meta-package (all-in-one) |

### Extras

```bash
# Provider-specific
pip install "miu-core[anthropic]"
pip install "miu-core[google]"
pip install "miu-core[openai]"

# All providers
pip install "miu-core[all]"

# Full bundle with web UI
pip install "miu-mono[all]"
```

## Features

- **Multi-Provider Support:** Anthropic Claude, Google Gemini, OpenAI GPT
- **ReAct Agent:** Reasoning and acting loop with tool execution
- **Rich Tool System:** File operations, code execution, web search
- **Multiple Interfaces:** CLI, TUI (Textual), Web UI (FastAPI)
- **OpenTelemetry Tracing:** Built-in observability
- **MCP Integration:** Model Context Protocol support
- **Extensible Hooks:** Customize agent behavior

## Configuration

Set your API keys:

```bash
# Anthropic (default)
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# OpenAI
export OPENAI_API_KEY="sk-..."
```

## Development

```bash
# Clone repository
git clone https://github.com/vanducng/miumono.git
cd miumono

# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and type check
uv run ruff check .
uv run mypy packages/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api/)
- [Examples](docs/examples.md)

## License

MIT
