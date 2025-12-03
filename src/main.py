from mcp_server.http_server import BrapiMcpHttpServer
from config.value import config
import uvicorn

if __name__ == '__main__':
  http_server = BrapiMcpHttpServer.create_server(config)
  uvicorn.run(http_server.app, host='0.0.0.0', port=config.port, reload=False)
