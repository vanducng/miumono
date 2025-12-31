"""Shared fixtures for code package tests."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from miu_core.memory import ShortTermMemory
from miu_core.modes import AgentMode, ModeManager
from miu_core.tools import ToolContext, ToolRegistry
from miu_core.usage import UsageTracker


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def ctx(temp_dir: Path) -> ToolContext:
    """Create tool context with temp working directory."""
    return ToolContext(working_dir=str(temp_dir))


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create empty tool registry."""
    return ToolRegistry()


@pytest.fixture
def memory() -> ShortTermMemory:
    """Create short-term memory for testing."""
    return ShortTermMemory()


@pytest.fixture
def mode_manager() -> ModeManager:
    """Create mode manager with default mode."""
    return ModeManager()


@pytest.fixture
def mode_manager_plan() -> ModeManager:
    """Create mode manager in plan mode."""
    return ModeManager(AgentMode.PLAN)


@pytest.fixture
def usage_tracker() -> UsageTracker:
    """Create usage tracker with default limits."""
    return UsageTracker()


@pytest.fixture
def usage_tracker_100k() -> UsageTracker:
    """Create usage tracker with 100k token limit."""
    return UsageTracker(context_limit=100_000)


@pytest.fixture
def sample_python_file(temp_dir: Path) -> Path:
    """Create sample Python file for testing."""
    file_path = temp_dir / "sample.py"
    file_path.write_text("""def hello():
    print("Hello, World!")

def goodbye():
    print("Goodbye!")

class MyClass:
    def __init__(self):
        self.value = 42
""")
    return file_path


@pytest.fixture
def sample_config_file(temp_dir: Path) -> Path:
    """Create sample config file for testing."""
    file_path = temp_dir / "config.json"
    file_path.write_text('{"key": "value", "count": 42}')
    return file_path


@pytest.fixture
def nested_dir_structure(temp_dir: Path) -> Path:
    """Create nested directory structure for glob/grep tests."""
    # Create directories
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "utils").mkdir()
    (temp_dir / "tests").mkdir()

    # Create files
    (temp_dir / "src" / "main.py").write_text("# Main module\ndef main(): pass")
    (temp_dir / "src" / "utils" / "helpers.py").write_text("# Helpers\ndef helper(): pass")
    (temp_dir / "tests" / "test_main.py").write_text("# Tests\ndef test_main(): pass")
    (temp_dir / "README.md").write_text("# Project\n")

    return temp_dir


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Create mock LLM provider."""
    provider = AsyncMock()
    provider.name = "mock"
    provider.model = "mock-model"
    return provider


@pytest.fixture
def home_dir() -> str:
    """Get home directory path."""
    return os.path.expanduser("~")


@pytest.fixture
def cwd() -> str:
    """Get current working directory."""
    return os.getcwd()
