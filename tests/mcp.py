from inline_snapshot import snapshot
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.tools.tool import Tool
from sweetpotatoquery import server
import pytest

# Running tests: pytest tests/mcp.py
# Adding snapshots: pytest tests/mcp.py --inline-snapshot=fix,create

@pytest.fixture
async def mcp_client():
  async with Client(transport=server) as mcp_client:
    yield mcp_client

@pytest.mark.asyncio
async def test_list_tools(mcp_client: Client[FastMCPTransport]):
    list_tools = await mcp_client.list_tools()

    assert len(list_tools) == 3

# TODO :: Automate output capturing through snapshot()
# @pytest.mark.asyncio
# async def test_list_tools(mcp_client: Client[FastMCPTransport]):
#     list_tools = await mcp_client.list_tools()

#     assert list_tools == snapshot()