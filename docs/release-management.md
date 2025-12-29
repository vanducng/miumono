# Release Management & Release-Please Configuration

**Project:** miu-mono
**Version:** 0.1.0
**Last Updated:** 2025-12-30

## Overview

miu-mono uses **Release-Please** for automated versioning, changelog generation, and release management. Release-Please automates the release workflow by creating pull requests that update versions and changelogs based on conventional commits.

## Configuration Files

### .release-please-manifest.json

Tracks current version for each package in the monorepo:

```json
{
  "packages/miu_core": "0.1.0",
  "packages/miu_code": "0.1.0",
  "packages/miu_examples": "0.1.0",
  "packages/miu_studio": "0.1.0",
  "packages/miu_mono": "0.1.0"
}
```

**Purpose:** Version source of truth. Release-Please updates this when creating release PRs.

**Location:** Repository root (`.release-please-manifest.json`)

### release-please-config.json

Main Release-Please configuration:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": { ... },
  "separate-pull-requests": true,
  "include-component-in-tag": true,
  "tag-separator": "-"
  ...
}
```

**Key Settings:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `release-type` | `python` | Semver + pyproject.toml updates |
| `package-name` | e.g., `miu-core` | PyPI package name |
| `changelog-path` | `CHANGELOG.md` | Per-package changelog location |
| `separate-pull-requests` | `true` | Individual PR per package release |
| `include-component-in-tag` | `true` | Tag format: `miu-core-v0.1.1` |
| `tag-separator` | `-` | Component/version separator |

**Location:** Repository root (`release-please-config.json`)

## Supported Commit Types

Release-Please categorizes commits into changelog sections:

| Type | Section | Example |
|------|---------|---------|
| `feat` | Features | New functionality |
| `fix` | Bug Fixes | Bug fixes |
| `perf` | Performance Improvements | Performance optimizations |
| `refactor` | Code Refactoring | Refactoring without behavior change |
| `docs` | Documentation | Doc changes (hidden in changelog) |
| `chore` | Miscellaneous | Build, deps, etc. (hidden in changelog) |

**Conventional Commit Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**
```bash
# Feature commit
git commit -m "feat(agent): add streaming support"

# Bug fix
git commit -m "fix(tools): resolve file path validation issue"

# Breaking change (triggers major version bump)
git commit -m "feat(api): redesign provider interface

BREAKING CHANGE: Provider.execute() renamed to Provider.invoke()"
```

## Release Workflow

### Automated Release Process

1. **Commit Code** using conventional commits
   ```bash
   git commit -m "feat(tools): add new tool feature"
   ```

2. **Release-Please Creates PR** (automated via GitHub Actions or manual trigger)
   - Analyzes commits since last release
   - Updates versions (semantic versioning)
   - Generates/updates CHANGELOG.md
   - Updates pyproject.toml files
   - Creates separate PR per package

3. **Review & Merge** the release PR
   - Verify changelog accuracy
   - Review version bumps
   - Merge to main branch

4. **GitHub Release** created automatically
   - Tags the commit
   - Publishes release notes
   - Triggers PyPI publication (with CI/CD)

### Manual Release Trigger

To manually trigger releases (if not using GitHub Actions):

```bash
# Using Release-Please CLI
npx release-please release-pr \
  --repo-url=https://github.com/vanducng/miu-mono \
  --token=$GITHUB_TOKEN

# Create releases
npx release-please github-release \
  --repo-url=https://github.com/vanducng/miu-mono \
  --token=$GITHUB_TOKEN
```

## Monorepo Package Management

Each package in miu-mono is independently versioned:

```
packages/
├── miu_core/        → miu-core package
├── miu_code/        → miu-code package
├── miu_examples/    → miu-examples package
├── miu_studio/      → miu-studio package
└── miu/             → miu meta-package
```

### Per-Package Configuration

Each package has:
- **CHANGELOG.md** - Tracks package-specific changes
- **pyproject.toml** - Contains version info
- **release-please config** - Separate section in `release-please-config.json`

### Tag Format

With `include-component-in-tag: true` and `tag-separator: "-"`:

```
miu-core-v0.1.1      # miu_core package
miu-code-v0.2.0      # miu_code package (major bump)
miu-v1.0.0           # miu meta-package
```

## Version Strategy (Semantic Versioning)

Release-Please implements **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH
  │      │      └─ Bug fixes, patches (fix: commits)
  │      └──────── New features (feat: commits)
  └───────────── Breaking changes (BREAKING CHANGE footer)
```

**Examples:**
- `0.1.0` → `0.1.1` (patch fix)
- `0.1.1` → `0.2.0` (new feature)
- `0.2.0` → `1.0.0` (breaking change)

## CHANGELOG Generation

Each package maintains its own CHANGELOG.md with structure:

```markdown
# Changelog

## [0.2.0](link) (2025-12-30)

### Features
* add streaming support ([abc1234](link))
* improve error handling ([def5678](link))

### Bug Fixes
* resolve file validation issue ([ghi9012](link))

### Code Refactoring
* simplify tool registry ([jkl3456](link))

## [0.1.0](link) (2025-12-29)

### Features
* initial release
```

**Auto-generated sections:**
1. Links to commits
2. Dates and version tags
3. Contributor mentions
4. Grouped by commit type

## CI/CD Integration

### Two-Workflow Approach

Miumono uses two coordinated workflows for releases:

1. **release-please.yml** - Creates release PRs and GitHub releases
2. **release.yml** - Publishes packages to PyPI

#### Release-Please Workflow

Workflow file: `.github/workflows/release-please.yml`

**Name:** Release Please

**Triggers:**
- Push to main branch
- Manual workflow dispatch (`workflow_dispatch`)

**Permissions:**
- `contents: write` - Create releases and tags
- `pull-requests: write` - Create and update PRs

**Jobs:**

1. **release-please** - Runs Release-Please action
   - Analyzes conventional commits
   - Creates release PRs per package
   - Creates GitHub releases and tags
   - Outputs per-package metadata

2. **trigger-publish** - Logs released packages
   - Informational job that runs when releases created
   - Provides visibility into which packages were released

**Key Outputs:**
- `releases_created` - Boolean: releases created
- `paths_released` - Comma-separated package paths
- Per-package: `<package>--release_created`, `<package>--tag_name`

#### Publish Workflow (Phase 2A)

Workflow file: `.github/workflows/release.yml`

**Name:** Publish to PyPI

**Trigger:**
- GitHub release event with type `[published]`
- Manual workflow dispatch with package selection

**Permissions:**
- `id-token: write` - OIDC trusted publishing

**Key Features:**
- Per-package matrix builds and publishing
- Test PyPI support via `workflow_dispatch`
- Artifacts managed per package
- Trusted publishing with OIDC (no token storage)

**Jobs:**

1. **determine-package** - Extract package from release tag
   - Parses release tag format: `package-name-vX.Y.Z`
   - Routes to appropriate package
   - Supports manual selection via `workflow_dispatch`

2. **build** - Matrix job builds each package
   - One job per package
   - Builds using `uv build`
   - Uploads artifacts by package

3. **publish-testpypi** - Optional Test PyPI publishing
   - Triggered by manual `workflow_dispatch` with `test_pypi: true`
   - Validates package before production release

4. **publish-pypi** - Production publishing
   - Triggered by release event or manual workflow
   - Uses PyPA trusted publishing (OIDC)
   - Publishes from artifacts

## Development Workflow

### Writing Commits

Always use conventional commits:

```bash
# Feature
git commit -m "feat(agent): add message streaming"

# Bug fix
git commit -m "fix(bash): handle shell errors gracefully"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Breaking changes
git commit -m "feat(api): redesign tool interface

BREAKING CHANGE: Tool.execute() signature changed to Tool.run(context)"
```

### Before Committing

1. Ensure code follows standards in `docs/code-standards.md`
2. Run tests: `uv run pytest`
3. Type check: `uv run mypy packages/`
4. Lint: `uv run ruff check .`
5. Format: `uv run ruff format .`

## Troubleshooting

### Issue: Release-Please PR Not Created

**Cause:** No commits with conventional format since last release

**Solution:**
```bash
# Ensure new commits use conventional format
git commit -m "feat(xyz): description"
```

### Issue: Wrong Version Bumped

**Cause:** Commit type doesn't match intended change

**Solution:** Check commit messages match actual changes:
- `feat:` for new features (minor bump)
- `fix:` for bug fixes (patch bump)
- Add `BREAKING CHANGE:` footer for major bumps

### Issue: CHANGELOG Has Wrong Content

**Cause:** Release-Please scans commit messages

**Solution:** Ensure conventional commits before release PR creation

### Issue: Monorepo Packages Don't Release

**Cause:** `separate-pull-requests: true` requires PR merge per package

**Solution:** Merge release PR to trigger all package releases

## Best Practices

1. **Use Conventional Commits** - Enables automated versioning
2. **Atomic Commits** - One logical change per commit
3. **Clear Scopes** - Use commit scope to identify area (e.g., `feat(tools)`)
4. **Breaking Changes** - Always use footer for breaking changes
5. **Review Releases** - Check generated CHANGELOG before merging
6. **Tag Releases** - GitHub releases provide audit trail
7. **Monitor Versions** - Keep `.release-please-manifest.json` in sync

## GitHub Workflow Integration

### release-please.yml Workflow

Located at: `.github/workflows/release-please.yml`

**When it runs:**
1. Push to main branch (automatic)
2. Manual trigger via GitHub UI (workflow_dispatch)

**What it does:**
1. Analyzes commits since last release using conventional commits
2. Creates separate PR per package with changes
3. Outputs release metadata (created flags, package paths, tags)
4. Triggers publish job to handle PyPI publication

**How to manually trigger:**
- Go to GitHub → Actions → Release Please
- Click "Run workflow" → Select main branch

### Workflow Outputs

Per-package release information available as workflow outputs:

```
miu-core--release_created: true/false
miu-core--tag_name: miu-core-v0.2.0

miu-code--release_created: true/false
miu-code--tag_name: miu-code-v0.1.1

# ... for all 5 packages
```

Use in downstream jobs via: `${{ needs.release-please.outputs.<output_name> }}`

## PyPI Trusted Publisher Configuration

To publish packages to PyPI using OIDC trusted publishing:

1. **For each package**, configure PyPI trusted publisher (COMPLETE as of 2025-12-30):
   - Project: https://pypi.org/project/{package-name}/
   - Settings → Trusted Publishers → Add
   - GitHub repository: `vanducng/miu-mono`
   - Workflow: `.github/workflows/release.yml`
   - Environment: `pypi`

2. **Optional TestPyPI setup** (for testing):
   - Same steps for https://test.pypi.org/project/{package-name}/
   - Environment: `testpypi`

See `docs/deployment-guide.md` for detailed PyPI setup instructions.

## Related Documentation

- **Code Standards:** See `docs/code-standards.md` for commit message style
- **Deployment:** See `docs/deployment-guide.md` for PyPI publication, trusted publisher setup, and publish workflow
- **Contributing:** See `CONTRIBUTING.md` for contributor guidelines and release section
- **CI/CD:** All workflows in `.github/workflows/`
  - `release-please.yml` - Release PR and GitHub release creation
  - `release.yml` - PyPI package publication with OIDC
  - `ci.yml` - Tests and linting
  - `pr-title-check.yml` - PR title conventional commit validation

## Resources

- [Release-Please Documentation](https://github.com/googleapis/release-please)
- [Release-Please Action](https://github.com/googleapis/release-please-action)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Document Status:** Phase 3C (Validation Complete)
**Approval Status:** Complete - Release-Please + OIDC trusted publishing verified
**Maintainer:** Development Team
**Last Review:** 2025-12-30
**Phase 3C Updates:**
- Added PyPI trusted publisher configuration section
- Verified all 5 packages use correct naming: miu-core, miu-code, miu-examples, miu-studio, miu
- Confirmed tag format: {package}-v{version} (e.g., miu-core-v1.0.0)
- Cross-referenced deployment-guide.md for detailed OIDC setup
- No breaking changes - validation-only phase
