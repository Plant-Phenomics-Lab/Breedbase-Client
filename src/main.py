from mcp_server.mcp_server import BrapiMcpServer
from config.value import config

server = BrapiMcpServer(config).create_server()

if __name__ == "__main__":
    server.run(transport="streamable-http", port=config.port)