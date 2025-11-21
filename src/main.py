from mcp_server.mcp_server import BrapiMcpServer
from config.type import BrapiServerConfig
from config.value import CONFIG

config = BrapiServerConfig(**CONFIG)
server = BrapiMcpServer(config).create_server()

if __name__ == "__main__":
    server.run(transport="streamable-http")