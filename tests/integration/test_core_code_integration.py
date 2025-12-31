"""Integration tests for core + code package interaction."""

import tempfile
from pathlib import Path

import pytest

from miu_code.tools import EditTool, GlobTool, GrepTool, ReadTool, WriteTool
from miu_core.agents.react import ReActAgent
from miu_core.models import Response, TextContent, ToolUseContent
from miu_core.providers.base import LLMProvider
from miu_core.tools import ToolContext, ToolRegistry


class TestCoreCodeToolIntegration:
    """Test core tool framework with code package tools."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def ctx(self, temp_dir: Path) -> ToolContext:
        return ToolContext(working_dir=str(temp_dir))

    @pytest.fixture
    def registry_with_code_tools(self) -> ToolRegistry:
        """Registry with code package tools."""
        registry = ToolRegistry()
        registry.register(ReadTool())
        registry.register(WriteTool())
        registry.register(EditTool())
        registry.register(GlobTool())
        registry.register(GrepTool())
        return registry

    @pytest.mark.asyncio
    async def test_write_then_read_file(
        self, temp_dir: Path, ctx: ToolContext, registry_with_code_tools: ToolRegistry
    ) -> None:
        """Test writing and reading a file through tool registry."""
        file_path = str(temp_dir / "test.txt")

        # Write file (tool name is "Write" with capital W)
        write_result = await registry_with_code_tools.execute(
            "Write", ctx, file_path=file_path, content="Hello, World!"
        )
        assert write_result.success

        # Read file (tool name is "Read" with capital R)
        read_result = await registry_with_code_tools.execute("Read", ctx, file_path=file_path)
        assert read_result.success
        assert "Hello, World!" in read_result.output

    @pytest.mark.asyncio
    async def test_write_edit_read_workflow(
        self, temp_dir: Path, ctx: ToolContext, registry_with_code_tools: ToolRegistry
    ) -> None:
        """Test complete file edit workflow."""
        file_path = str(temp_dir / "code.py")

        # Write initial content
        await registry_with_code_tools.execute(
            "Write", ctx, file_path=file_path, content="def hello():\n    print('hello')"
        )

        # Edit content
        edit_result = await registry_with_code_tools.execute(
            "Edit",
            ctx,
            file_path=file_path,
            old_string="hello",
            new_string="world",
            replace_all=True,
        )
        assert edit_result.success

        # Verify changes
        read_result = await registry_with_code_tools.execute("Read", ctx, file_path=file_path)
        assert "world" in read_result.output
        assert "hello" not in read_result.output

    @pytest.mark.asyncio
    async def test_glob_finds_written_files(
        self, temp_dir: Path, ctx: ToolContext, registry_with_code_tools: ToolRegistry
    ) -> None:
        """Test glob finds files created by write tool."""
        # Create multiple files
        for i in range(3):
            file_path = str(temp_dir / f"file{i}.py")
            await registry_with_code_tools.execute(
                "Write", ctx, file_path=file_path, content=f"# File {i}"
            )

        # Glob for python files
        glob_result = await registry_with_code_tools.execute("Glob", ctx, pattern="*.py")
        assert glob_result.success
        assert "file0.py" in glob_result.output
        assert "file1.py" in glob_result.output
        assert "file2.py" in glob_result.output

    @pytest.mark.asyncio
    async def test_grep_finds_content_in_written_files(
        self, temp_dir: Path, ctx: ToolContext, registry_with_code_tools: ToolRegistry
    ) -> None:
        """Test grep finds content in files created by write tool."""
        # Create files with specific content
        await registry_with_code_tools.execute(
            "Write",
            ctx,
            file_path=str(temp_dir / "main.py"),
            content="def main():\n    pass",
        )
        await registry_with_code_tools.execute(
            "Write",
            ctx,
            file_path=str(temp_dir / "utils.py"),
            content="def helper():\n    pass",
        )

        # Grep for function definitions
        grep_result = await registry_with_code_tools.execute("Grep", ctx, pattern=r"def \w+")
        assert grep_result.success
        assert "main" in grep_result.output
        assert "helper" in grep_result.output


class TestCoreCodeAgentIntegration:
    """Test ReAct agent using code package tools."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def registry_with_read(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(ReadTool())
        return registry

    @pytest.mark.asyncio
    async def test_agent_can_read_file(
        self, temp_dir: Path, registry_with_read: ToolRegistry
    ) -> None:
        """Test agent uses read tool to access file content."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Important content")

        call_count = [0]

        class FileReadProvider(LLMProvider):
            name = "file-reader"
            model = "test"

            async def complete(self, messages, tools=None, system=None, max_tokens=4096):
                call_count[0] += 1
                if call_count[0] == 1:
                    return Response(
                        id="resp-1",
                        content=[
                            ToolUseContent(
                                id="t1",
                                name="Read",  # Tool name is "Read" with capital R
                                input={"file_path": str(test_file)},
                            )
                        ],
                        stop_reason="tool_use",
                    )
                # File content should be in previous messages
                return Response(
                    id="resp-2",
                    content=[TextContent(text="File content received")],
                    stop_reason="end_turn",
                )

        provider = FileReadProvider()
        agent = ReActAgent(
            provider=provider,
            tools=registry_with_read,
            working_dir=str(temp_dir),
        )

        response = await agent.run("Read the test file")
        assert response.get_text() == "File content received"
        assert call_count[0] == 2
