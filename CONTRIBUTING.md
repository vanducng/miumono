# Contributing to Miumono

Thank you for your interest in contributing to miu! This document provides guidelines for contributing.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Development Setup

```bash
# Clone the repository
git clone https://github.com/vanducng/miumono.git
cd miumono

# Install dependencies
uv sync

# Verify setup
uv run pytest
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write tests for new functionality
- Follow the existing code style
- Update documentation if needed

### 3. Run Checks

Before submitting, ensure all checks pass:

```bash
# Lint
uv run ruff check .
uv run ruff format --check .

# Type check
uv run mypy packages/

# Tests
uv run pytest
```

### 4. Commit Changes

Use conventional commit messages:

```
feat: add new tool for file operations
fix: resolve agent iteration limit
docs: update API reference
test: add tests for provider factory
refactor: simplify tool manager
```

### 5. Submit Pull Request

- Push your branch to GitHub
- Open a PR against `main`
- Fill in the PR template
- Wait for CI to pass
- Request review

## Code Style

### Python

- **Type hints:** Required on all public APIs
- **Docstrings:** Google style
- **Line length:** 100 characters
- **Imports:** Sorted by ruff

Example:

```python
def create_agent(
    provider: str,
    model: str,
    *,
    system_prompt: str | None = None,
) -> BaseAgent:
    """Create an agent with the specified provider.

    Args:
        provider: Provider name (anthropic, google, openai).
        model: Model identifier.
        system_prompt: Optional system prompt override.

    Returns:
        Configured agent instance.

    Raises:
        ValueError: If provider is not supported.
    """
    ...
```

### Tests

- Place tests in `packages/<name>/tests/`
- Use descriptive test names
- Mock external services

```python
def test_agent_executes_tool_successfully():
    """Agent should execute tools and return results."""
    ...
```

## Package Structure

When adding new features, follow the existing structure:

```
packages/<name>/
├── pyproject.toml
├── <name>/
│   ├── __init__.py
│   └── <module>.py
└── tests/
    └── test_<module>.py
```

## Documentation

- Update docstrings for API changes
- Add examples for new features
- Keep README files current

## Reporting Issues

When reporting bugs:

1. Check existing issues first
2. Include Python version and OS
3. Provide minimal reproduction steps
4. Include error messages/stack traces

## Questions?

- Open a [GitHub Discussion](https://github.com/vanducng/miumono/discussions)
- Check existing documentation in `docs/`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
