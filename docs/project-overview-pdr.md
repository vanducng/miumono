# Miumono - Project Overview & PDR

**Project Name:** Miumono - AI Agent Framework Monorepo
**Version:** 0.1.0 (MVP Tier 1 Delivered)
**Status:** Phase 4 Complete - TUI Integration Finished
**Last Updated:** 2025-12-30

## Executive Summary

Miumono is a Python-based AI agent framework designed to simplify building AI-powered coding assistants. It provides a modular, extensible architecture for integrating multiple LLM providers (Anthropic Claude, OpenAI, Google Gemini) with code manipulation tools, enabling developers to create intelligent agents that can read, modify, and execute code.

## Vision & Goals

### Vision
Enable developers to build production-grade AI agents that understand code and can safely operate on codebases through a clean, extensible framework.

### Goals (MVP Tier 1)
1. Establish modular architecture separating core framework from CLI agents
2. Support multiple LLM providers via unified interface
3. Provide safe file and shell execution tools
4. Enable interactive and batch usage modes
5. Ensure code quality through strict type safety and testing

## Product Development Requirements (PDR)

### Functional Requirements

#### FR-1: Multi-Provider LLM Support
- **Requirement:** Framework must support Anthropic Claude, OpenAI, and Google Gemini
- **Acceptance Criteria:**
  - All three providers have working implementations
  - Unified interface abstracts provider differences
  - Easy provider switching via configuration
- **Status:** Core implemented, CLI integration in progress

#### FR-2: Core Tool Ecosystem
- **Requirement:** Provide foundational tools for agent operations
- **Tools Required:**
  - File reading (read)
  - File writing (write)
  - File editing (edit)
  - Shell command execution (bash)
  - File pattern matching (glob)
  - Content search (grep)
- **Acceptance Criteria:**
  - All tools implement consistent interface
  - Each tool has test coverage
  - Tools include error handling and safety checks
- **Status:** All tools implemented

#### FR-3: CLI Interface
- **Requirement:** Command-line interface for agent interaction
- **Features:**
  - One-shot query mode: `miu -q "query"` or `miu --query "query"`
  - Interactive REPL mode: `miu`
  - Interactive TUI mode: `miu code`
  - Session persistence
- **Acceptance Criteria:**
  - CLI is installable via pip/uv
  - All modes work correctly (REPL, TUI, one-shot)
  - Session data persists between runs
- **Status:** Implemented (Phase 1 CLI Fix Complete)

#### FR-4: Agent Architecture
- **Requirement:** Core agent framework supporting ReAct pattern
- **Components:**
  - Base Agent class
  - ReAct Agent implementation
  - Tool registry and execution
  - Message history management
- **Acceptance Criteria:**
  - Agents can execute tools in loop
  - Proper error handling and recovery
  - Type-safe tool invocation
- **Status:** Core framework implemented

### Non-Functional Requirements

#### NFR-1: Code Quality
- **Type Safety:** Strict MyPy mode for all code
- **Testing:** Minimum 80% code coverage
- **Style:** Ruff linting with formatting
- **Python Version:** 3.11+
- **Status:** Standards defined, enforcement in CI/CD needed

#### NFR-2: Performance
- **Async Operations:** All I/O must be non-blocking
- **Tool Execution:** Tools must complete within reasonable timeouts
- **Memory:** Agents should efficiently manage message history
- **Status:** Framework supports async patterns

#### NFR-3: Extensibility
- **Provider Plugin System:** Easy to add new LLM providers
- **Tool Registry:** Simple tool registration and discovery
- **Agent Customization:** Subclass ReActAgent for custom behavior
- **Status:** Architecture supports extensibility

#### NFR-4: Security
- **File Operations:** Validate paths to prevent directory traversal (implemented Phase 01)
- **Shell Execution:** Use subprocess with proper escaping (implemented Phase 01)
- **Provider Keys:** Use environment variables for credentials (env: ANTHROPIC_API_KEY, etc)
- **CORS Restriction:** Hardened to localhost only, configurable via MIU_CORS_ORIGINS (Phase 01)
- **Rate Limiting:** 10 req/min on API endpoints via slowapi (Phase 01)
- **Input Validation:** Session IDs (UUID), message sizes (64KB max), script paths (Phase 01)
- **Security Headers:** CSP, Cache-Control on responses (Phase 01)
- **Status:** Phase 01 security hardening complete

#### NFR-5: Documentation
- **API Documentation:** All public APIs must be documented
- **Usage Examples:** Each major feature needs examples
- **Deployment Guide:** Clear setup and deployment instructions
- **Status:** Basic docs created, comprehensive docs in progress

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│                    Miumono CLI                       │
│  (Interactive REPL + One-shot Query Interface)       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  Coding Agent                        │
│  (miu_code package - AI agent with coding tools)     │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  Core Framework                      │
│  (miu_core package - Agent abstraction & tools)      │
├─────────────────────────────────────────────────────┤
│  • Agent Base Classes                               │
│  • Tool Registry                                    │
│  • LLM Provider Interface                           │
│  • Data Models                                      │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌────▼──────┐ ┌──▼────────┐
│  Anthropic  │ │   OpenAI   │ │  Google   │
│   Claude    │ │            │ │  Gemini   │
└─────────────┘ └────────────┘ └───────────┘
```

### Package Structure

**miu-core:**
- Core agent framework
- Provider integrations
- Tool abstractions
- Data models
- No CLI dependencies

**miu-code:**
- Coding agent implementation
- CLI interface
- Tool implementations (read, write, edit, bash, glob, grep)
- Session management
- Depends on miu-core

## Implementation Phases (PHASE 4 ACTIVE)

### Tier 1 MVP Deliverables (Completed Phase 1A)
- [x] Workspace setup with UV monorepo
- [x] Package structure (miu_core, miu_code)
- [x] Core agent framework with ReAct pattern
- [x] Provider implementations (Anthropic, OpenAI, Google)
- [x] Tool registry system with 6 core tools
- [x] File/shell tools (read, write, edit, bash, glob, grep)
- [x] CLI interface (one-shot + interactive REPL)
- [x] Session management and persistence
- [x] Basic documentation and README
- [x] Code quality tooling (Ruff, MyPy, Pytest)
- [x] Type-safe implementations across codebase

### Phase 1B (Testing & Comprehensive Docs) - COMPLETE
- [x] Integration test coverage
- [x] Comprehensive API documentation
- [x] Deployment guide completion
- [x] Security audit and fixes
- [x] Example applications
- [x] Release-Please configuration

### Phase 2 (Mode Management & Usage Tracking) - COMPLETE
- [x] ModeManager for mode cycling (NORMAL → PLAN → ASK)
- [x] UsageTracker for token usage statistics
- [x] Integration with core framework

### Phase 3 (TUI Widgets) - COMPLETE
- [x] StatusBar widget with mode/path/usage display
- [x] WelcomeBanner widget with metadata
- [x] ChatLog widget for message display
- [x] LoadingSpinner widget
- [x] 40+ widget tests

### Phase 4 (TUI Integration) - COMPLETE
- [x] MiuCodeApp main application
- [x] Real-time streaming event handling
- [x] Token usage tracking in streaming
- [x] Mode cycling with shift+tab
- [x] Session management (ctrl+n, ctrl+l)
- [x] MessageStopEvent.usage field
- [x] Usage propagation in Anthropic provider

### Phase 01 - Security Hardening (COMPLETE)
- [x] CORS restriction to localhost (env: MIU_CORS_ORIGINS)
- [x] Rate limiting (10 req/min on chat endpoints via slowapi)
- [x] Session ID validation (UUID format across API)
- [x] Message size limits (64KB max to prevent DoS)
- [x] Script path validation (whitelist allowed dirs in hook executor)
- [x] MCP JSON size limits (10MB max to prevent memory exhaustion)
- [x] CSP and security headers (Content-Security-Policy on static content)
- [x] slowapi dependency added to miu-studio

### Phase 1C & Beyond - PLANNED
- [ ] CI/CD pipeline (GitHub Actions) with release automation
- [ ] PyPI release automation via GitHub Actions (DONE for v0.1.0)
- [ ] Web UI interface (miu-studio Phase 4B complete)
- [ ] Advanced debugging tools
- [ ] Plugin system architecture
- [ ] Performance benchmarking

## Technical Specifications

### Python Version & Dependencies
- **Python:** 3.11+
- **Package Manager:** UV (monorepo workspace)
- **Build System:** hatchling

### Development Tools
- **Linting:** Ruff (100 char lines)
- **Type Checking:** MyPy (strict mode)
- **Testing:** Pytest with asyncio support
- **Version Control:** Git

### Supported Platforms
- macOS (Darwin)
- Linux
- Windows (through WSL)

## Success Criteria

### Phase 1A Completion (ACHIEVED)
- [x] All packages buildable and installable
- [x] Type checking passes without errors (MyPy strict mode)
- [x] Linting and formatting compliant (Ruff)
- [x] Basic documentation complete
- [x] CLI functional and usable
- [x] All core tools implemented and working
- [x] Multi-provider support functional

### Quality Metrics Achieved
- Type Safety: 100% MyPy strict compliance
- Code Quality: Ruff compliant across all packages
- Package Structure: Clean monorepo with workspace management
- Documentation: Overview, standards, and architecture documented

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| API changes in dependencies | High | Medium | Pin major versions, monitor releases |
| Performance issues at scale | Medium | Low | Load testing, async patterns |
| Security vulnerabilities | High | Low | Regular audits, dependency scanning |
| LLM provider rate limits | Medium | Low | Implement caching, rate limiting |
| Integration issues | Medium | Medium | Comprehensive testing, CI/CD |

## Dependencies & Constraints

### Critical Dependencies
- pydantic (data validation)
- httpx (async HTTP)
- anthropic (primary provider)

### Version Constraints
- Python ≥3.11
- Pydantic ≥2.0
- httpx ≥0.27

### External Dependencies
- Anthropic API
- OpenAI API
- Google Gemini API

## Resource Requirements

### Development Team
- Lead Developer: 1
- Code Review: Peer review process
- Testing: Automated via CI/CD

### Infrastructure
- Git repository (GitHub)
- CI/CD platform (GitHub Actions)
- Package registry (PyPI)

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Phase 1A - Workspace Setup & MVP Tier 1 | 2025-12-29 | COMPLETE |
| Phase 1B - Testing & Comprehensive Docs | 2026-01-15 | Next |
| Phase 1C - CI/CD & Release Automation | 2026-02-01 | Planned |
| MVP Release (v0.1.0) to PyPI | 2026-02-15 | Planned |

## Next Steps

1. Complete comprehensive documentation
2. Implement integration tests
3. Setup GitHub Actions CI/CD
4. Perform security audit
5. Release v0.1.0 to PyPI

---

**Document Status:** PHASE 1A COMPLETE
**Approval Status:** APPROVED FOR PHASE 1B
**Maintainer:** Development Team
**Last Review:** 2025-12-29
**Phase 1A Completion Date:** 2025-12-29
