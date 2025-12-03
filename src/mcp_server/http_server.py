from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes
from config.type import BrapiServerConfig
from mcp_server.mcp_server import BrapiMcpServer

class BrapiMcpHttpServer:
  _instance = None

  def __init__(self, config: BrapiServerConfig):
    if hasattr(self, '_initialized') and self._initialized:
      return
    self.mcp_base = BrapiMcpServer(config)
    self.mcp_app = self.mcp_base.create_server().http_app(path='/mcp')

    self.app = FastAPI(title='BrAPI MCP Server', lifespan=self.mcp_app.lifespan)
    self._setup_routes()
    self.app.mount('/', self.mcp_app)
    self._initialized = True

  def _setup_routes(self):
    """Setup HTTP routes for file downloads"""

    @self.app.get('/download/{session_id}/{result_id}')
    async def download_result(session_id: str, result_id: str):
      """
      Download a cached result file.

      URL: http://localhost:8000/download/{session_id}/{result_id}
      """
      # Get cache for session
      caches = self.mcp_base.session_manager.caches
      if session_id not in caches:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

      cache = caches[session_id]
      info = cache.get_result_info(result_id)

      if not info:
        raise HTTPException(status_code=404, detail=f"Result '{result_id}' not found")

      file_path = Path(info['file_path'])

      if not file_path.exists():
        raise HTTPException(status_code=404, detail='File not found on disk')

      # Determine MIME type
      mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

      # Return file for download
      return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=f'{result_id}.{info["format"]}',
        headers={'Content-Disposition': f'attachment; filename={result_id}.{info["format"]}'},
      )

  @classmethod
  def create_server(cls, config: BrapiServerConfig):
    if cls._instance is None:
      cls._instance = cls(config)
    return cls._instance
