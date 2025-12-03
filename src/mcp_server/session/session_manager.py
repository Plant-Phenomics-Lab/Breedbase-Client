"""Persistent session management"""

from fastmcp import Context
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime
from mcp_server.session.result_cache import ResultCache


class SessionManager:
  """
  Manages sessions with disk persistence.
  Sessions survive server restarts.
  """

  def __init__(self, base_cache_dir: Path):
    self.base_cache_dir = base_cache_dir
    self.base_cache_dir.mkdir(parents=True, exist_ok=True)

    self.registry_file = base_cache_dir / 'sessions.json'
    self.caches: Dict[str, ResultCache] = {}

    self._load_registry()

  def _load_registry(self):
    """Load session registry from disk"""
    if self.registry_file.exists():
      with open(self.registry_file, 'r') as f:
        self.registry = json.load(f)
    else:
      self.registry = {}

  def _save_registry(self):
    """Persist session registry to disk"""
    with open(self.registry_file, 'w') as f:
      json.dump(self.registry, f, indent=2)

  def get_or_create_session(
    self, session_id: Optional[str] = None, context: Optional[Context] = None
  ) -> tuple[ResultCache, str]:
    """
    Get or create a session.
    Returns (cache, session_id)

    Session lookup order:
    1. Explicit session_id parameter
    2. MCP context session_id
    3. Create new session
    """
    # Determine session ID
    if session_id:
      final_session_id = session_id
    elif context and hasattr(context, 'session_id'):
      final_session_id = context.session_id
    else:
      # Create new session
      import uuid

      final_session_id = str(uuid.uuid4())[:8]

    # Check if session exists in registry
    if final_session_id not in self.registry:
      # Create new session entry
      self.registry[final_session_id] = {
        'created_at': datetime.now().isoformat(),
        'last_accessed': datetime.now().isoformat(),
        'cache_dir': str(self.base_cache_dir / final_session_id),
      }
      self._save_registry()
    else:
      # Update last accessed time
      self.registry[final_session_id]['last_accessed'] = datetime.now().isoformat()
      self._save_registry()

    # Get or create cache instance
    if final_session_id not in self.caches:
      cache_dir = Path(self.registry[final_session_id]['cache_dir'])
      self.caches[final_session_id] = ResultCache(cache_dir)

    return self.caches[final_session_id], final_session_id

  def get_session_info(self, session_id: str) -> Optional[Dict]:
    """Get session metadata"""
    return self.registry.get(session_id)

  def list_sessions(self) -> Dict[str, Dict]:
    """List all sessions"""
    return self.registry

  def session_exists(self, session_id: str) -> bool:
    """Check if session exists"""
    return session_id in self.registry
