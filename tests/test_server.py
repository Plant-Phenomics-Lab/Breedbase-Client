import os
import sys

import pytest
from fastmcp.client import Client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.value import config  # noqa: E402
from mcp_server.mcp_server import BrapiMcpServer  # noqa: E402

# These tests build the real server, which introspects the BrAPI server at BASE_URL
# (defaults to the public SweetPotatoBase instance), so they require network access.

EXPECTED_TOOLS = {
  'brapi_get',
  'brapi_search',
  'describe_server_capabilities',
  'download_images',
  'get_download_instructions',
  'get_image_search_parameters',
  'get_result_summary',
  'get_search_parameters',
  'load_result',
  'quick_download_link',
}


@pytest.fixture
async def mcp_client():
  server = BrapiMcpServer(config).create_server()
  async with Client(server) as client:
    yield client


async def test_list_tools(mcp_client: Client):
  tools = await mcp_client.list_tools()
  assert {t.name for t in tools} == EXPECTED_TOOLS
