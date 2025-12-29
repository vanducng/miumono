"""MCP client example demonstrating MCP server integration.

Run with:
    python -m miu_examples.mcp_client

This example shows how to connect to an MCP server and use its tools.

Requires:
    An MCP server running (e.g., mcp-server-filesystem)
"""

import asyncio

from miu_core.mcp import MCPClient


async def main() -> None:
    """Demonstrate MCP client usage."""
    # Example: Connect to a filesystem MCP server
    # Note: You need to have an MCP server running for this to work
    print("MCP Client Example")
    print("=" * 40)

    # Create client for stdio transport
    # In production, replace with actual server command
    server_command = ["npx", "-y", "@anthropic-ai/mcp-server-filesystem", "."]

    try:
        async with MCPClient(command=server_command) as client:
            # Initialize connection
            init_response = await client.initialize(
                client_name="miu-examples",
                client_version="0.1.0",
            )
            print(f"Connected to: {init_response.server_info.name}")
            print(f"Server version: {init_response.server_info.version}")

            # List available tools
            tools = await client.list_tools()
            print(f"\nAvailable tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:50]}...")

            # Call a tool (if filesystem server)
            if any(t.name == "read_file" for t in tools.tools):
                print("\nReading README.md...")
                result = await client.call_tool(
                    "read_file",
                    {"path": "README.md"},
                )
                print(f"Result: {result.content[:200]}...")

    except FileNotFoundError:
        print("Error: MCP server not found.")
        print("Install with: npm install -g @anthropic-ai/mcp-server-filesystem")
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        print("\nThis example requires an MCP server to be available.")
        print("Try running with a different MCP server or ensure npx is installed.")


if __name__ == "__main__":
    asyncio.run(main())
