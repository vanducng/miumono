# Changelog

## [1.0.1](https://github.com/vanducng/miu-mono/compare/miu-core-v1.0.0...miu-core-v1.0.1) (2026-01-01)


### Bug Fixes

* **core:** use 'is not None' for optional parameter defaults ([342e79c](https://github.com/vanducng/miu-mono/commit/342e79c6487044e49debfa015a9d04183a44f469))
* **docs:** update schema format, rename to MIU, increase logo size ([427de92](https://github.com/vanducng/miu-mono/commit/427de92d111cc78e369fd804cd1c09d4cd725bab))


### Code Refactoring

* **core:** implement DRY patterns for providers and sessions ([ebee863](https://github.com/vanducng/miu-mono/commit/ebee8635d1f679980c8bfa62c60b884790650b01))

## [1.0.0](https://github.com/vanducng/miu-mono/compare/miu-core-v0.2.0...miu-core-v1.0.0) (2025-12-31)


### ⚠ BREAKING CHANGES

* Package folder paths changed, but no API changes.

### Code Refactoring

* simplify package folder names ([08206dc](https://github.com/vanducng/miu-mono/commit/08206dc3d0d90c3a31bf45a4e78561df639c40be))

## [0.2.0](https://github.com/vanducng/miu-mono/compare/miu-core-v0.1.0...miu-core-v0.2.0) (2025-12-29)


### Features

* **tier1:** implement Phase 1A workspace setup ([281db61](https://github.com/vanducng/miu-mono/commit/281db61b62b6306a389a88d8f4764c0b03cacc6c))
* **tier2:** implement enhanced UX with multi-provider, memory, skills, hooks, TUI ([76e471b](https://github.com/vanducng/miu-mono/commit/76e471bb4c41d024905a95d1ba05d7d182f17447))
* **tier3:** implement protocols & integration (MCP, ACP, commands, logging) ([bfbe6d2](https://github.com/vanducng/miu-mono/commit/bfbe6d251f9fecb7a00df7e3137df79460063009))
* **tier4:** fix all mypy type checking errors ([1957028](https://github.com/vanducng/miu-mono/commit/195702843d196095652b88bbec637f8c1a9de437))
* **tier4:** implement Phase 4F - OpenTelemetry Integration ([f3b8b59](https://github.com/vanducng/miu-mono/commit/f3b8b59094e4cfb252d3d9566d0339527caa97b9))
* **tier4:** implement Phase 4H - multi-agent patterns ([5dbaa9d](https://github.com/vanducng/miu-mono/commit/5dbaa9d84e85800781b95aae26b87503c5822290))


### Bug Fixes

* **miu-core:** resolve mypy type errors and add pre-commit config ([09896fa](https://github.com/vanducng/miu-mono/commit/09896faece9dbf896cfd3c80b8c3f642b04da057))
