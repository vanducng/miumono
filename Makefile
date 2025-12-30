# Miumono Development Makefile
# Usage: make <target>

.PHONY: help install dev-tui dev-install dev-watch test lint format typecheck all

# Default target
help:
	@echo "Miumono Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install all dependencies with uv sync"
	@echo "  dev-install   Install packages in editable mode"
	@echo ""
	@echo "Development:"
	@echo "  dev-tui       Run TUI (miu code)"
	@echo "  dev-watch     Watch for changes and re-run TUI"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-tui      Run TUI-specific tests"
	@echo "  test-cov      Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run ruff check"
	@echo "  format        Run ruff format"
	@echo "  typecheck     Run mypy"
	@echo "  all           Run lint + typecheck + test"

# Setup
install:
	uv sync

dev-install:
	uv pip install -e packages/miu_core -e packages/miu_code

# Development
dev-tui:
	uv run miu code

dev-watch:
	@echo "Watching for changes... (Ctrl+C to stop)"
	@while true; do \
		uv run miu code; \
		echo "TUI exited. Restarting in 1s..."; \
		sleep 1; \
	done

# Testing
test:
	uv run pytest

test-tui:
	uv run pytest packages/miu_code/tests/tui/ -v

test-cov:
	uv run pytest --cov=packages/miu_core --cov=packages/miu_code

# Code Quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy packages/miu_core packages/miu_code

all: lint typecheck test
	@echo "All checks passed!"
