# miu-mono Project Roadmap

**Project:** AI Agent Framework Monorepo
**Version:** 0.2.0 (miu-code), 0.1.0 (others)
**Last Updated:** 2025-12-30

## Release Timeline

### Phase 1A: MVP Tier 1 - Workspace Setup (COMPLETE)
**Status:** DELIVERED 2025-12-29

**Scope:**
- Core framework with agent abstractions
- Multi-provider LLM support (Anthropic, OpenAI, Google)
- Tool registry and 6 core tools
- CLI interface (one-shot + interactive REPL)
- Session management
- Code quality standards

**Deliverables:**
- `miu-core` package: Framework library
- `miu-code` package: CLI agent
- Documentation: overview, standards, architecture
- Type-safe codebase (MyPy strict mode)
- Ruff-compliant formatting

---

### Phase 1B: Testing & Comprehensive Documentation
**Status:** NEXT (Target: 2026-01-15)

**Scope:**
- Integration test coverage
- Comprehensive API documentation
- Deployment and setup guides
- Security audit and fixes
- Example applications

**Deliverables:**
- Integration test suite with 80%+ coverage
- API reference documentation
- Deployment guide
- Security assessment report
- 3-5 example implementations
- Contributing guidelines

---

### Phase 1C: CI/CD & Release Automation
**Status:** COMPLETE (2025-12-30)

**Scope:**
- GitHub Actions CI/CD pipeline
- Automated testing on multiple Python versions
- PyPI release automation
- Version management automation
- Release notes generation

**Deliverables:**
- GitHub Actions workflow configuration
- PyPI package publishing
- Automated testing matrix
- Version bump tooling
- Release checklist automation

**Progress Notes:**
- Release-please implementation COMPLETE (all 6 phases DONE as of 2025-12-30)
  - Phase 3A: Archive Legacy Scripts - COMPLETE (2025-12-30)
    - Scripts renamed: bump_version.py → manual_bump_version.py
    - Scripts renamed: release.py → manual_release.py
    - Documentation updated (release-management.md, scripts/README.md)
    - Fallback-only status clearly documented
  - Phase 3B: Documentation Updates - COMPLETE (2025-12-30)
  - Phase 3C: Validation Testing - COMPLETE (2025-12-30)
    - All JSON/YAML configs validated
    - Package structure verified (5 packages)
    - Tag patterns confirmed unique
    - 95/95 tests passed
    - Code review: 0 critical issues
- Separate PRs per package enabled for independent versioning
- Conventional commits enforcement added
- Legacy manual scripts archived with new names
- Ready for first release-please run

---

### MVP Release: v0.1.0 to PyPI
**Status:** COMPLETE (Delivered 2025-12-30)

**Deliverables COMPLETED:**
- `miu-core==0.1.0` published to PyPI (https://pypi.org/project/miu-core/)
- `miu-code==0.1.0` published to PyPI (https://pypi.org/project/miu-code/)
- `miu-examples==0.1.0` published to PyPI (https://pypi.org/project/miu-examples/)
- `miu-studio==0.1.0` published to PyPI (https://pypi.org/project/miu-studio/)
- `miu-mono==0.1.0` published to PyPI (https://pypi.org/project/miu-mono/)
- PyPI trusted publishers configured for OIDC
- Repository renamed to miu-mono
- GitHub release with release notes
- Installation guide
- Quick start documentation

---

## Phase 4: Refactoring & DRY
**Status:** COMPLETE (2026-01-01)

**Scope:**
- DRY refactoring to eliminate provider duplication
- Session storage abstraction with pluggable backends
- Token-aware memory truncation with model-specific ratios
- CI security scanning integration

**Deliverables:**
- `miu_core.providers.converters` module (shared utilities for message/response conversion)
- `miu_core.session` module (abstract base + JSONL implementation)
- Improved `miu_core.memory.truncation` with model-specific token ratios (claude: 3.5, gpt: 4.0, gemini: 3.8)
- GitHub Actions security job (Bandit + pip-audit)
- Code standards documentation updated

**Artifacts:**
- `/packages/core/miu_core/providers/converters.py` (NEW)
- `/packages/core/miu_core/session/base.py` (NEW)
- `/packages/core/miu_core/session/jsonl.py` (NEW)
- `/packages/core/miu_core/memory/truncation.py` (IMPROVED)
- `/.github/workflows/ci.yml` (UPDATED - security job added)
- `/docs/code-standards.md` (UPDATED - Phase 04 patterns)

**Impact:**
- Reduced 126+ LOC duplication across provider implementations
- Flexible session storage (can add DB, S3, etc. backends)
- More accurate token estimation per LLM model
- Proactive security monitoring in CI/CD

---

## Phase 5: TUI Vibe Refactor
**Status:** COMPLETE (2025-12-30)

**Scope:**
- Add Makefile for dev command convenience
- Upgrade Textual dependency to v1.0.0+ (stability & features)
- Maintain TUI widget integration (Phase 3-4 features)

**Deliverables:**
- Makefile with 12 dev commands (help, install, dev-tui, test, lint, etc.)
- miu-code pyproject.toml: textual dependency updated >=0.90 → >=1.0.0
- Documentation updated (codebase-summary.md, project-roadmap.md)
- miu-code version bumped to v0.2.0

**Artifacts:**
- `/Makefile` (NEW)
- `/packages/miu_code/pyproject.toml` (UPDATED)
- `/docs/codebase-summary.md` (UPDATED)

---

## Phase 2: Enhanced Features (2026 Q1)

### Phase 2A: Advanced Tooling
- Debugging tools (step, breakpoint, inspect)
- Code analysis tools (lint, format, test)
- Git integration tools
- Docker/container support

### Phase 2B: Web UI
- Web dashboard for agent management
- Real-time execution monitoring
- Session visualization
- Built-in documentation viewer

### Phase 2C: Enterprise Features
- Comprehensive logging system
- Metrics and monitoring
- Audit trail
- Rate limiting and quotas

---

## Phase 3: Ecosystem (2026 Q2+)

### Plugin System
- Plugin marketplace
- Custom provider registration
- Custom tool development framework
- Community contributions support

### Performance & Optimization
- Response caching
- Token optimization
- Connection pooling
- Memory-efficient message history

### Additional LLM Providers
- Claude 4 / Claude 5 (upcoming)
- Other provider support based on demand
- Custom on-premises LLM support

---

## Feature Status Matrix

| Feature | Phase | Status | Priority |
|---------|-------|--------|----------|
| Core framework | 1A | COMPLETE | P0 |
| Multi-provider support | 1A | COMPLETE | P0 |
| CLI interface | 1A | COMPLETE | P0 |
| Core tools (6) | 1A | COMPLETE | P0 |
| Session management | 1A | COMPLETE | P0 |
| Type safety | 1A | COMPLETE | P0 |
| TUI widgets (Phase 3) | 3 | COMPLETE | P0 |
| TUI integration (Phase 4) | 4 | COMPLETE | P0 |
| Makefile + Textual 1.0 (Phase 5) | 5 | COMPLETE | P0 |
| Provider converters & DRY refactor (Phase 4) | 4 | COMPLETE | P0 |
| Session storage abstraction (Phase 4) | 4 | COMPLETE | P0 |
| Token-aware memory truncation (Phase 4) | 4 | COMPLETE | P0 |
| CI security scanning (Phase 4) | 4 | COMPLETE | P0 |
| Integration tests | 1B | PENDING | P0 |
| API documentation | 1B | PENDING | P0 |
| Security audit | 1B | PENDING | P1 |
| CI/CD pipeline | 1C | PENDING | P1 |
| PyPI release | 1C | PENDING | P1 |
| Debugging tools | 2A | PLANNED | P2 |
| Web UI | 2B | PLANNED | P2 |
| Enterprise logging | 2C | PLANNED | P3 |
| Plugin system | 3 | PLANNED | P3 |

---

## Known Issues & Technical Debt

### Phase 1A
- None identified (initial implementation)

### Phase 1B Priority
1. Comprehensive integration test coverage needed
2. Security audit for file/shell operations
3. API documentation completion
4. Error handling improvements

### Phase 2+ Considerations
1. Performance optimization for large codebases
2. Streaming response support for large outputs
3. Advanced caching strategies
4. Multi-language support planning

---

## Dependency & Tool Status

| Tool | Version | Status | Notes |
|------|---------|--------|-------|
| Python | 3.11+ | Stable | Minimum supported version |
| UV | Latest | Stable | Package manager & monorepo |
| Pydantic | 2.0+ | Stable | Data validation |
| AsyncClick | 8.1+ | Stable | CLI framework |
| Anthropic SDK | 0.40+ | Active | Primary provider |
| OpenAI SDK | 1.50+ | Active | Secondary provider |
| Google GenAI | 0.8+ | Active | Tertiary provider |
| Pytest | 8.0+ | Stable | Testing framework |
| MyPy | 1.13+ | Stable | Type checking |
| Ruff | 0.8+ | Active | Linting/formatting |

---

## Success Metrics

### Phase 1A (COMPLETED)
- [x] 2 packages (miu-core, miu-code) created
- [x] 3 LLM providers integrated
- [x] 6 core tools implemented
- [x] CLI functional (one-shot + interactive)
- [x] Type-safe codebase (100% MyPy compliance)
- [x] Code quality standards (Ruff compliant)

### Phase 1B (TARGET)
- [ ] 80%+ test coverage across packages
- [ ] All public APIs documented
- [ ] Security audit completed
- [ ] 3+ example applications
- [ ] Zero high-severity issues

### Phase 1C (TARGET)
- [ ] Automated CI/CD pipeline active
- [ ] All tests run on Python 3.11, 3.12, 3.13
- [ ] Automated PyPI releases
- [ ] Release automation tested and verified

### MVP Release (TARGET)
- [ ] Published on PyPI
- [ ] 50+ GitHub stars
- [ ] Community contributions started
- [ ] Documentation >90% complete

---

## Communication & Coordination

**Repository:** https://github.com/vanducng/miu-mono
**Documentation:** ./docs/
**Issues:** GitHub Issues
**Discussions:** GitHub Discussions

---

**Document Status:** ACTIVE
**Maintainer:** Development Team
**Last Review:** 2026-01-01 (Phase 4 Complete)
**Next Review:** 2026-01-08
