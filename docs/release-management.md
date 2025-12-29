# Release Management & Release-Please Configuration

**Project:** Miumono
**Version:** 0.1.0
**Last Updated:** 2025-12-29

## Overview

Miumono uses **Release-Please** for automated versioning, changelog generation, and release management. Release-Please automates the release workflow by creating pull requests that update versions and changelogs based on conventional commits.

## Configuration Files

### .release-please-manifest.json

Tracks current version for each package in the monorepo:

```json
{
  "packages/miu_core": "0.1.0",
  "packages/miu_code": "0.1.0",
  "packages/miu_examples": "0.1.0",
  "packages/miu_studio": "0.1.0",
  "packages/miu": "0.1.0"
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
  --repo-url=https://github.com/vanducng/miumono \
  --token=$GITHUB_TOKEN

# Create releases
npx release-please github-release \
  --repo-url=https://github.com/vanducng/miumono \
  --token=$GITHUB_TOKEN
```

## Monorepo Package Management

Each package in Miumono is independently versioned:

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

### GitHub Actions Setup (Recommended)

Create `.github/workflows/release.yml`:

```yaml
on:
  push:
    branches: [main]

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

### PyPI Publication

After release, publish with:

```bash
# Requires: PyPI token in GitHub secrets
uv build
uv publish --token ${{ secrets.PYPI_TOKEN }}
```

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

## Related Documentation

- **Code Standards:** See `docs/code-standards.md` for commit message style
- **Deployment:** See `docs/deployment-guide.md` for PyPI publication
- **CI/CD:** Workflows in `.github/workflows/`

## Resources

- [Release-Please Documentation](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Document Status:** Phase 1A Complete
**Approval Status:** Ready for Phase 1B
**Maintainer:** Development Team
**Last Review:** 2025-12-29
