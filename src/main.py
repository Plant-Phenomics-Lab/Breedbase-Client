import uvicorn
import threading
import sys
import os
import time
import http.client

# Ensure 'src' is in the path so local imports work regardless of execution directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.value import config
from mcp_server.http_server import BrapiMcpHttpServer
from mcp_server.mcp_server import BrapiMcpServer
from utils.maintenance import cleanup_old_files

def run_http_server(host: str, log_level: str):
    """Runs the HTTP server (blocking)"""
    http_server = BrapiMcpHttpServer.create_server(config)
    # Run uvicorn with specified host and log level
    # In stdio mode, log_level='error' suppresses access logs to keep stdout clean
    uvicorn.run(http_server.app, host=host, port=config.port, log_level=log_level)

def wait_for_http(port: int, timeout: int = 10) -> bool:
    """Wait for HTTP server to be responsive"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port)
            conn.request("GET", "/health")
            response = conn.getresponse()
            if response.status == 200:
                conn.close()
                return True
            conn.close()
        except Exception:
            pass
        time.sleep(0.1)
    return False

if __name__ == '__main__':
    # Perform maintenance cleanup on startup
    # This ensures old logs/downloads are removed regardless of how the server stops
    cleanup_old_files(config, days=30)

    if config.mode.lower() == 'stdio':
        
        # 1. Start HTTP server in a background thread (Daemon)
        # Bind to 127.0.0.1 for security in local mode
        # Use 'error' log level to keep stdout clean for MCP
        http_thread = threading.Thread(
            target=run_http_server, 
            args=("127.0.0.1", "error"), 
            daemon=True
        )
        http_thread.start()

        # 2. Wait for HTTP server to be ready
        # This ensures we don't advertise URLs before they are reachable
        if not wait_for_http(config.port):
            sys.stderr.write(f"Error: HTTP server failed to start on port {config.port}\n")
            sys.exit(1)

        # 3. Run the MCP server in Stdio mode (Main Thread)
        # This blocks until the MCP connection closes
        mcp_server = BrapiMcpServer(config).create_server()
        mcp_server.run()
        
    else:
        # Standard HTTP Mode (Server only)
        # Bind to 0.0.0.0 to allow external access if needed
        # Use 'info' log level for visibility
        run_http_server("0.0.0.0", "info")
