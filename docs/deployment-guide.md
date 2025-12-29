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

## GitHub Actions Workflows (Phase 2A)

### 1. Release-Please Workflow

File: `.github/workflows/release-please.yml`

Auto-creates release PRs and GitHub releases on push to main:

**Triggers:**
- Push to main branch
- Manual trigger via `workflow_dispatch`

**Key Jobs:**
- `release-please` - Analyzes commits, creates release PRs, generates GitHub releases
- `trigger-publish` - Informational job logging released packages

**Outputs:**
- `releases_created` - Boolean flag
- `paths_released` - Comma-separated list of released package paths
- Per-package outputs: `<package>--release_created`, `<package>--tag_name`

### 2. Publish Workflow (Phase 2A - Complete)

File: `.github/workflows/release.yml`

Publishes packages to PyPI using per-package matrix strategy:

**Trigger:**
- `release` event with type `[published]` (from release-please)
- Manual trigger via `workflow_dispatch` with package selection

**Permissions:**
- `id-token: write` - OIDC trusted publishing

**Key Jobs:**

**determine-package** - Extracts package from release tag:
- Parses tag format: `miu-core-v0.1.0` → `miu_core`
- Routes to appropriate package
- Supports manual input via `workflow_dispatch`

**build** - Matrix job, one per package:
- Checks out code
- Installs uv
- Builds with `uv build packages/{package}`
- Uploads artifacts per package

**publish-testpypi** - Optional validation publishing:
- Triggered by manual `workflow_dispatch` with `test_pypi: true`
- Tests package before production
- Uses TestPyPI repository

**publish-pypi** - Production publishing:
- Triggered by release event or manual workflow (test_pypi false)
- Uses PyPA gh-action-pypi-publish with OIDC
- Downloads artifacts and publishes each package
- No token storage - OIDC trusted publishing

**Advantages:**
- Per-package isolation and error handling
- Trusted publishing (OIDC) - no PyPI token in secrets
- Test PyPI support for pre-release validation
- Release-less manual publish capability
- Clean separation: release-please creates releases, publish workflow publishes

### Workflow Sequence

```
1. Developer pushes commits (conventional format)
   ↓
2. release-please.yml triggers on main push
   ↓
3. Release-Please creates release PR(s) per package
   ↓
4. Developer reviews & merges PR
   ↓
5. GitHub creates release (automatic, release-please)
   ↓
6. release.yml triggers on release event
   ↓
7. determine-package extracts package from tag
   ↓
8. build matrix creates per-package artifacts
   ↓
9. publish-pypi publishes all to PyPI (OIDC)
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

- **Release-Please Setup:** `docs/release-management.md` (detailed config, workflow outputs, troubleshooting)
- **Code Standards:** `docs/code-standards.md` (conventional commits, commit message style)
- **CI/CD Workflows:** `.github/workflows/`
  - `release-please.yml` - Release PR and GitHub release creation (Phase 1B)
  - `publish.yml` - PyPI publication (recommended to create)
  - `ci.yml` - Tests and linting

## Resources

- [Release-Please GitHub](https://github.com/googleapis/release-please)
- [Release-Please Action](https://github.com/googleapis/release-please-action)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Help](https://pypi.org/help/)
- [UV Documentation](https://docs.astral.sh/uv/)

---

**Document Status:** Phase 2A (Publish Workflow Complete)
**Approval Status:** Complete - OIDC trusted publishing implemented
**Maintainer:** Development Team
**Last Review:** 2025-12-29
**Phase 2A Updates:**
- Documented release.yml with per-package matrix strategy
- Updated trigger from tag push to release event
- Documented OIDC trusted publishing (no token storage)
- Documented test PyPI support via workflow_dispatch
