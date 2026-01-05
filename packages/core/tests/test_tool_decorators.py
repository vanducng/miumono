"""Tests for decorator-based tool definitions."""

import pytest

from miu_core.tools import FunctionTool, ToolContext, ToolRegistry, ToolResult, sync_tool, tool


class TestToolDecorator:
    """Tests for @tool decorator."""

    def test_basic_tool_creation(self) -> None:
        """Test creating a tool from a simple async function."""

        @tool()
        async def greet(name: str) -> str:
            """Say hello to someone."""
            return f"Hello, {name}!"

        assert isinstance(greet, FunctionTool)
        assert greet.name == "greet"
        assert "hello" in greet.description.lower()

    def test_custom_name_and_description(self) -> None:
        """Test tool with custom name and description."""

        @tool(name="custom_greet", description="Custom greeting tool")
        async def greet(name: str) -> str:
            return f"Hi, {name}!"

        assert greet.name == "custom_greet"
        assert greet.description == "Custom greeting tool"

    def test_tool_schema_generation(self) -> None:
        """Test that input schema is correctly generated."""

        @tool()
        async def add(a: int, b: int = 0) -> int:
            """Add two numbers."""
            return a + b

        schema = add.get_input_schema()
        json_schema = schema.model_json_schema()

        assert "a" in json_schema["properties"]
        assert "b" in json_schema["properties"]
        assert "a" in json_schema["required"]
        assert "b" not in json_schema.get("required", [])

    def test_tool_schema_with_optional_params(self) -> None:
        """Test schema with optional parameters."""

        @tool()
        async def read_file(
            path: str,
            encoding: str = "utf-8",
            limit: int | None = None,
        ) -> str:
            """Read a file."""
            return f"Reading {path}"

        schema = read_file.get_input_schema()
        json_schema = schema.model_json_schema()

        assert "path" in json_schema["properties"]
        assert "encoding" in json_schema["properties"]
        assert "limit" in json_schema["properties"]

    @pytest.mark.asyncio
    async def test_tool_execution(self) -> None:
        """Test executing a decorated tool."""

        @tool()
        async def multiply(x: int, y: int) -> int:
            """Multiply two numbers."""
            return x * y

        ctx = ToolContext()
        result = await multiply.execute(ctx, x=5, y=3)

        assert result.success
        assert "15" in result.output

    @pytest.mark.asyncio
    async def test_tool_with_context(self) -> None:
        """Test tool that uses context."""

        @tool()
        async def get_working_dir(ctx: ToolContext) -> str:
            """Get the working directory."""
            return ctx.working_dir

        ctx = ToolContext(working_dir="/test/path")
        result = await get_working_dir.execute(ctx)

        assert result.success
        assert "/test/path" in result.output

    @pytest.mark.asyncio
    async def test_tool_returns_tool_result(self) -> None:
        """Test tool that returns ToolResult directly."""

        @tool()
        async def check_status(value: int) -> ToolResult:
            """Check if value is positive."""
            if value > 0:
                return ToolResult(output="Value is positive")
            else:
                return ToolResult(
                    output="Value is not positive",
                    success=False,
                    error="Non-positive value",
                )

        ctx = ToolContext()

        result = await check_status.execute(ctx, value=5)
        assert result.success
        assert "positive" in result.output

        result = await check_status.execute(ctx, value=-1)
        assert not result.success
        assert result.error == "Non-positive value"

    @pytest.mark.asyncio
    async def test_tool_error_handling(self) -> None:
        """Test tool error handling."""

        @tool()
        async def fail_tool(message: str) -> str:
            """A tool that always fails."""
            raise ValueError(message)

        ctx = ToolContext()
        result = await fail_tool.execute(ctx, message="Test error")

        assert not result.success
        assert "Test error" in result.error or ""

    def test_non_async_function_raises(self) -> None:
        """Test that non-async functions raise TypeError."""
        with pytest.raises(TypeError, match="must be an async function"):

            @tool()
            def sync_func(x: int) -> int:  # type: ignore[misc]
                return x * 2

    def test_tool_to_schema(self) -> None:
        """Test converting tool to LLM-compatible schema."""

        @tool(description="Calculate sum of two numbers")
        async def add(a: float, b: float) -> float:
            return a + b

        schema = add.to_schema()

        assert schema["name"] == "add"
        assert schema["description"] == "Calculate sum of two numbers"
        assert "input_schema" in schema
        assert "a" in schema["input_schema"]["properties"]
        assert "b" in schema["input_schema"]["properties"]


class TestSyncToolDecorator:
    """Tests for @sync_tool decorator."""

    def test_sync_tool_creation(self) -> None:
        """Test creating a tool from a sync function."""

        @sync_tool(description="A sync calculator")
        def calculate(x: int, y: int) -> int:
            """Calculate x + y."""
            return x + y

        assert isinstance(calculate, FunctionTool)
        assert calculate.name == "calculate"

    @pytest.mark.asyncio
    async def test_sync_tool_execution(self) -> None:
        """Test executing a sync tool."""

        @sync_tool()
        def uppercase(text: str) -> str:
            """Convert text to uppercase."""
            return text.upper()

        ctx = ToolContext()
        result = await uppercase.execute(ctx, text="hello")

        assert result.success
        assert "HELLO" in result.output

    def test_async_function_raises_for_sync_tool(self) -> None:
        """Test that async functions raise TypeError for sync_tool."""
        with pytest.raises(TypeError, match="is async, use @tool instead"):

            @sync_tool()
            async def async_func(x: int) -> int:
                return x * 2


class TestToolRegistryIntegration:
    """Tests for registry integration with decorated tools."""

    def test_register_decorated_tool(self) -> None:
        """Test registering a decorated tool."""

        @tool()
        async def echo(message: str) -> str:
            """Echo the message."""
            return message

        registry = ToolRegistry()
        registry.register(echo)

        assert registry.get("echo") is echo
        assert len(registry) == 1

    def test_get_schemas_with_decorated_tools(self) -> None:
        """Test getting schemas from registry with decorated tools."""

        @tool()
        async def tool_a(x: int) -> int:
            return x

        @tool()
        async def tool_b(y: str) -> str:
            return y

        registry = ToolRegistry()
        registry.register(tool_a)
        registry.register(tool_b)

        schemas = registry.get_schemas()
        assert len(schemas) == 2

        names = {s["name"] for s in schemas}
        assert "tool_a" in names
        assert "tool_b" in names

    @pytest.mark.asyncio
    async def test_execute_decorated_tool_via_registry(self) -> None:
        """Test executing decorated tool through registry."""

        @tool()
        async def concat(a: str, b: str) -> str:
            """Concatenate strings."""
            return a + b

        registry = ToolRegistry()
        registry.register(concat)

        ctx = ToolContext()
        result = await registry.execute("concat", ctx, a="hello", b="world")

        assert result.success
        assert "helloworld" in result.output

    def test_mix_class_and_decorated_tools(self) -> None:
        """Test mixing class-based and decorated tools in registry."""
        from pydantic import BaseModel

        from miu_core.tools import Tool

        class EchoInput(BaseModel):
            message: str

        class ClassTool(Tool):
            name = "class_echo"
            description = "Class-based echo"

            def get_input_schema(self) -> type[BaseModel]:
                return EchoInput

            async def execute(self, ctx: ToolContext, message: str, **kwargs: object) -> ToolResult:
                return ToolResult(output=f"Class: {message}")

        @tool()
        async def func_echo(message: str) -> str:
            """Function-based echo."""
            return f"Func: {message}"

        registry = ToolRegistry()
        registry.register(ClassTool())
        registry.register(func_echo)

        assert len(registry) == 2
        assert registry.get("class_echo") is not None
        assert registry.get("func_echo") is not None


class TestToolSchemaTypes:
    """Tests for schema type handling."""

    def test_string_param(self) -> None:
        """Test string parameter schema."""

        @tool()
        async def greet(name: str) -> str:
            return f"Hello {name}"

        schema = greet.get_input_schema().model_json_schema()
        assert schema["properties"]["name"]["type"] == "string"

    def test_int_param(self) -> None:
        """Test integer parameter schema."""

        @tool()
        async def double(x: int) -> int:
            return x * 2

        schema = double.get_input_schema().model_json_schema()
        assert schema["properties"]["x"]["type"] == "integer"

    def test_float_param(self) -> None:
        """Test float parameter schema."""

        @tool()
        async def half(x: float) -> float:
            return x / 2

        schema = half.get_input_schema().model_json_schema()
        assert schema["properties"]["x"]["type"] == "number"

    def test_bool_param(self) -> None:
        """Test boolean parameter schema."""

        @tool()
        async def toggle(flag: bool) -> bool:
            return not flag

        schema = toggle.get_input_schema().model_json_schema()
        assert schema["properties"]["flag"]["type"] == "boolean"

    def test_list_param(self) -> None:
        """Test list parameter schema."""

        @tool()
        async def count(items: list) -> int:  # type: ignore[type-arg]
            return len(items)

        schema = count.get_input_schema().model_json_schema()
        assert schema["properties"]["items"]["type"] == "array"

    def test_dict_param(self) -> None:
        """Test dict parameter schema."""

        @tool()
        async def get_keys(data: dict) -> list:  # type: ignore[type-arg]
            return list(data.keys())

        schema = get_keys.get_input_schema().model_json_schema()
        assert schema["properties"]["data"]["type"] == "object"
