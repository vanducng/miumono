# Miumono - Project Overview & PDR

**Project Name:** Miumono - AI Agent Framework Monorepo
**Version:** 0.1.0 (MVP Tier 1 Delivered)
**Status:** Phase 1A Complete - Ready for Phase 1B
**Last Updated:** 2025-12-29

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
  - One-shot query mode: `miu "query"`
  - Interactive REPL mode: `miu`
  - Session persistence
- **Acceptance Criteria:**
  - CLI is installable via pip/uv
  - Both modes work correctly
  - Session data persists between runs
- **Status:** Implemented

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
- **File Operations:** Validate paths to prevent directory traversal
- **Shell Execution:** Use subprocess with proper escaping
- **Provider Keys:** Use environment variables for credentials
- **Status:** Initial security patterns in place, needs audit

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

## Implementation Phase (Phase 1A - COMPLETE)

### Tier 1 MVP Deliverables (Completed)
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

### Phase 1B - Next (Testing & Comprehensive Docs)
- [ ] Integration test coverage
- [ ] Comprehensive API documentation
- [ ] Deployment guide completion
- [ ] Security audit and fixes
- [ ] Example applications

### Phase 1C & Beyond
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] PyPI release automation
- [ ] Web UI interface
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
