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

## Releases

Releases are automated using [release-please](https://github.com/googleapis/release-please).

### How It Works

1. **Write commits using Conventional Commits format:**
   ```
   feat(miu-core): add new provider interface
   fix(miu-code): resolve CLI parsing issue
   docs(miu-studio): update API reference
   ```

2. **Push/merge to main branch**

3. **Review Release PR:**
   - release-please creates a PR per package with changes
   - PR includes version bump + changelog preview
   - Review and merge when ready to release

4. **Automatic Publishing:**
   - Merging release PR creates GitHub Release
   - PyPI publishing triggers automatically

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** feat, fix, docs, style, refactor, perf, test, chore, ci, build
**Scopes:** miu-core, miu-code, miu-examples, miu-studio, miu

### Version Bumps

| Commit Type | Version Change |
|-------------|---------------|
| `fix:` | Patch (0.0.X) |
| `feat:` | Minor (0.X.0) |
| `BREAKING CHANGE:` in footer | Major (X.0.0) |

### Independent Versioning

Each package is versioned independently:
- `miu-core-v1.2.0`
- `miu-code-v2.0.0`
- etc.

See [docs/release-management.md](docs/release-management.md) for detailed release process documentation.

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
