# Miumono

AI Agent Framework Monorepo.

## Packages

| Package | Description |
|---------|-------------|
| [miu-core](packages/miu_core/) | Core framework library |
| [miu-code](packages/miu_code/) | AI coding agent with CLI |

## Quick Start

```bash
# Install the CLI
uv add miu-code

# Run a query
miu "read package.json"

# Interactive mode
miu
```

## Development

```bash
# Install dependencies
uv sync

# Run linting
uv run ruff check .

# Run type checking
uv run mypy packages/

# Run tests
uv run pytest
```

## License

MIT
