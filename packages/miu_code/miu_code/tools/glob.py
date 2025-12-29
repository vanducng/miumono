"""Glob file pattern tool."""

from pathlib import Path

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult


class GlobInput(BaseModel):
    """Input for glob tool."""

    pattern: str = Field(description="Glob pattern to match files (e.g., '**/*.py')")
    path: str | None = Field(None, description="Base directory to search in")


class GlobTool(Tool):
    """Find files matching a glob pattern."""

    name = "Glob"
    description = "Find files matching a glob pattern. Use for discovering files by name/extension."

    def get_input_schema(self) -> type[BaseModel]:
        return GlobInput

    async def execute(  # type: ignore[override]
        self,
        ctx: ToolContext,
        pattern: str,
        path: str | None = None,
        **kwargs: object,
    ) -> ToolResult:
        """Find files matching pattern."""
        base = Path(path) if path else Path(ctx.working_dir)

        if not base.is_absolute():
            base = Path(ctx.working_dir) / base

        if not base.exists():
            return ToolResult(
                output=f"Directory not found: {base}",
                success=False,
                error="Directory does not exist",
            )

        try:
            matches = sorted(base.glob(pattern))
            matches = [m for m in matches if m.is_file()]

            if not matches:
                return ToolResult(output=f"No files match pattern: {pattern}")

            # Limit output to prevent overwhelming results
            max_files = 100
            if len(matches) > max_files:
                output_lines = [str(m) for m in matches[:max_files]]
                output_lines.append(f"... and {len(matches) - max_files} more files")
            else:
                output_lines = [str(m) for m in matches]

            return ToolResult(output="\n".join(output_lines))

        except ValueError as e:
            return ToolResult(
                output=f"Invalid pattern: {e}",
                success=False,
                error=str(e),
            )
