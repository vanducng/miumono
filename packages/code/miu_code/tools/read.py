"""Read file tool."""

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult

from .security import PathTraversalError, validate_path


class ReadInput(BaseModel):
    """Input for read tool."""

    file_path: str = Field(description="Absolute path to the file to read")
    offset: int | None = Field(None, description="Line offset (1-based) to start reading from")
    limit: int | None = Field(None, description="Maximum number of lines to read")


class ReadTool(Tool):
    """Read file contents with line numbers."""

    name = "Read"
    description = "Read file contents with line numbers. Use for viewing files."

    def get_input_schema(self) -> type[BaseModel]:
        return ReadInput

    async def execute(
        self,
        ctx: ToolContext,
        **kwargs: object,
    ) -> ToolResult:
        """Read file and return numbered lines."""
        # Extract and validate required arguments
        file_path = str(kwargs.get("file_path", ""))
        if not file_path:
            return ToolResult(
                output="Missing required argument: 'file_path'",
                success=False,
                error="file_path is required",
            )
        offset_val = kwargs.get("offset")
        offset = int(str(offset_val)) if offset_val is not None else None
        limit_val = kwargs.get("limit")
        limit = int(str(limit_val)) if limit_val is not None else None

        try:
            path = validate_path(file_path, ctx.working_dir)
        except PathTraversalError as e:
            return ToolResult(
                output=f"Access denied: {file_path}",
                success=False,
                error=str(e),
            )

        if not path.exists():
            return ToolResult(
                output=f"File not found: {file_path}",
                success=False,
                error=f"File does not exist: {file_path}",
            )

        if not path.is_file():
            return ToolResult(
                output=f"Not a file: {file_path}",
                success=False,
                error=f"Path is not a file: {file_path}",
            )

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(
                output=f"Cannot read binary file: {file_path}",
                success=False,
                error="Binary file",
            )

        lines = content.splitlines()

        # Apply offset and limit
        start = (offset - 1) if offset and offset > 0 else 0
        end = (start + limit) if limit else len(lines)
        selected = lines[start:end]

        # Format with line numbers
        numbered = [f"{i + start + 1:4d}│{line}" for i, line in enumerate(selected)]
        return ToolResult(output="\n".join(numbered))
