import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


MCP_SERVER_PATH = Path(__file__).parent / "mcp_server.py"


async def call_mcp_tool_async(tool_name, arguments):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            return result


def call_mcp_tool(tool_name, arguments):
    return asyncio.run(
        call_mcp_tool_async(
            tool_name,
            arguments
        )
    )