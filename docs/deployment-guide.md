# Deployment & Release Guide

**Project:** Miumono
**Version:** 0.1.0
**Last Updated:** 2025-12-29

## Overview

This guide covers deployment of Miumono packages to PyPI and managing releases using Release-Please. Miumono is a monorepo with five independently versioned packages distributed on PyPI.

## Package Structure

```
Miumono (Monorepo)
├── packages/miu_core/       → miu-core (core framework)
├── packages/miu_code/       → miu-code (CLI agent)
├── packages/miu_examples/   → miu-examples (example apps)
├── packages/miu_studio/     → miu-studio (web UI)
└── packages/miu/            → miu (meta-package)
```

Each package is independently versioned and released to PyPI.

## Release Process

### 1. Conventional Commits

All commits must follow Conventional Commits format. Release-Please uses commit types to determine version bumps:

**Format:** `<type>(<scope>): <description>`

```bash
# Feature - triggers MINOR version bump (0.1.0 → 0.2.0)
git commit -m "feat(agent): add streaming support"

# Bug fix - triggers PATCH version bump (0.1.0 → 0.1.1)
git commit -m "fix(tools): resolve validation bug"

# Breaking change - triggers MAJOR version bump (0.1.0 → 1.0.0)
git commit -m "feat(api): redesign Provider interface

BREAKING CHANGE: Provider.execute() renamed to Provider.invoke()"
```

**Valid Commit Types:**
- `feat` - Feature (minor bump, visible in changelog)
- `fix` - Bug fix (patch bump, visible in changelog)
- `perf` - Performance (patch bump, visible in changelog)
- `refactor` - Refactoring (patch bump, hidden from changelog)
- `docs` - Documentation (no version bump, hidden)
- `chore` - Maintenance (no version bump, hidden)

### 2. Release-Please Creates PR

When commits are pushed to `main`:

1. GitHub Actions triggers Release-Please workflow
2. Release-Please analyzes commits since last release
3. Creates separate PR for each package with changes:
   - Updates `pyproject.toml` version
   - Generates/updates `CHANGELOG.md`
   - Updates `.release-please-manifest.json`
   - PR title: `chore(miu-core): release 0.2.0`

### 3. Review & Merge

1. Review generated PR
   - Verify version bumps (semantic versioning)
   - Check CHANGELOG accuracy
   - Ensure no unintended changes

2. Merge to `main`
   - Triggers GitHub Actions to create release

3. GitHub creates release with:
   - Git tag (e.g., `miu-core-v0.2.0`)
   - Release notes from CHANGELOG
   - Artifact links

### 4. PyPI Publication

After release PR merges, publish to PyPI:

```bash
# Build all packages
uv build

# Publish to PyPI (requires PyPI token)
uv publish --token ${{ secrets.PYPI_TOKEN }}

# Verify publication
pip install --upgrade miu-code==0.2.0
```

## Configuration Files

### .release-please-manifest.json

Tracks current version for each package:

```json
{
  "packages/miu_core": "0.1.0",
  "packages/miu_code": "0.1.0",
  "packages/miu_examples": "0.1.0",
  "packages/miu_studio": "0.1.0",
  "packages/miu": "0.1.0"
}
```

Updated automatically by Release-Please when creating release PRs.

### release-please-config.json

Main Release-Please configuration (in repository root):

**Key Settings:**
- `release-type: python` - Semver + pyproject.toml updates
- `package-name` - PyPI package name (miu-core, miu-code, etc.)
- `changelog-path` - Per-package CHANGELOG.md
- `separate-pull-requests: true` - One PR per package
- `include-component-in-tag: true` - Tag format: `miu-core-v0.2.0`

See `docs/release-management.md` for complete configuration details.

## Manual Release (No CI/CD)

If GitHub Actions not available, trigger releases manually:

```bash
# Install Release-Please CLI
npm install -g release-please

# Create release PRs
release-please release-pr \
  --repo-url=https://github.com/vanducng/miumono \
  --token=$GITHUB_TOKEN

# Create GitHub releases and tags
release-please github-release \
  --repo-url=https://github.com/vanducng/miumono \
  --token=$GITHUB_TOKEN
```

## PyPI Publishing

### Prerequisites

1. PyPI account and token:
   ```bash
   # Create token at https://pypi.org/account/tokens/
   export PYPI_TOKEN="pypi-..."
   ```

2. GitHub Actions secret (if using CI/CD):
   - Add `PYPI_TOKEN` to repository secrets
   - GitHub Actions can then publish automatically

### Publishing Commands

**Build packages:**
```bash
# Build all packages
uv build

# Build specific package
cd packages/miu_core && uv build
```

**Publish to PyPI:**
```bash
# Publish all packages
uv publish --token $PYPI_TOKEN

# Publish specific package
cd packages/miu_code && uv publish --token $PYPI_TOKEN

# Test upload first (TestPyPI)
uv publish --publish-url https://test.pypi.org/legacy/ --token $TEST_PYPI_TOKEN
```

## GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  publish:
    needs: release-please
    if: ${{ needs.release-please.outputs.releases_created }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Build packages
        run: uv build

      - name: Publish to PyPI
        run: uv publish --token ${{ secrets.PYPI_TOKEN }}
```

## Monorepo Version Management

### Independent Versioning

Each package versions independently:
- miu-core: v0.2.0
- miu-code: v0.1.5
- miu-examples: v0.1.0
- miu-studio: v0.3.0
- miu: v0.2.0

This allows smaller packages to patch while larger ones develop features.

### Tag Format

With Release-Please configuration:
```
miu-core-v0.2.0       # miu_core package release
miu-code-v0.1.5       # miu_code patch release
miu-studio-v0.3.0     # miu_studio major feature
```

### Inter-package Dependencies

The meta-package `miu` pins specific versions of dependencies:

```toml
# packages/miu/pyproject.toml
dependencies = [
    "miu-core>=0.2.0,<1.0",
    "miu-code>=0.1.5,<1.0",
    "miu-examples>=0.1.0,<1.0",
    "miu-studio>=0.3.0,<1.0",
]
```

## Troubleshooting

### Release-Please PR Not Created

**Cause:** No commits with conventional format

**Solution:** Ensure commits use `feat:`, `fix:`, or `perf:` prefixes

### Wrong Version Bump

**Cause:** Commit type doesn't match intent

**Solution:**
- `feat:` → minor bump only
- `fix:` → patch bump
- `BREAKING CHANGE:` → major bump

### CHANGELOG Missing Entries

**Cause:** Commits not in conventional format

**Solution:** Check commit messages before release PR creation

### PyPI Publish Fails

**Cause:** Invalid token or already published version

**Solution:**
```bash
# Check token validity
curl -H "Authorization: Bearer $PYPI_TOKEN" https://pypi.org/pypi

# Check published version exists
pip index versions miu-code
```

### Build Failures

**Cause:** Missing dependencies or imports

**Solution:**
```bash
# Sync dependencies
uv sync

# Verify build
uv build --dry-run
```

## Version Release Checklist

- [ ] All commits use conventional format
- [ ] Tests pass: `uv run pytest --cov`
- [ ] Type check passes: `uv run mypy packages/`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Release-Please PR created and reviewed
- [ ] CHANGELOG entries accurate
- [ ] Version bumps correct (semantic versioning)
- [ ] PR merged to main
- [ ] GitHub release created automatically
- [ ] PyPI publication successful
- [ ] Verify installation: `pip install --upgrade miu-code`

## Related Documentation

- **Release-Please Setup:** `docs/release-management.md`
- **Code Standards:** `docs/code-standards.md` (conventional commits)
- **CI/CD Workflows:** `.github/workflows/`

## Resources

- [Release-Please GitHub](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Help](https://pypi.org/help/)
- [UV Documentation](https://docs.astral.sh/uv/)

---

**Document Status:** Phase 1A Complete
**Approval Status:** Ready for Phase 1B
**Maintainer:** Development Team
**Last Review:** 2025-12-29
