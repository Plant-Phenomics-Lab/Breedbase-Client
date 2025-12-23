from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class BrapiServerConfig:
  mode: str 
  port: int 
  name: str
  base_url: str
  authtype: Optional[str] = None
  username: Optional[str] = None
  password: Optional[str] = None
  session_dir_override: Optional[str] = None
  capabilities_override: Optional[Path] = None
  workspace_dir: Path = Path(__file__).parent.parent.parent

  # @property
  # def workspace_dir(self) -> Path:
  #     return Path(__file__).parent.parent.parent
  
  @property
  def log_dir(self) -> Path:
      d = self.workspace_dir / "cache" / self.name / "logs"
      d.mkdir(parents=True, exist_ok=True)
      return d

  @property
  def sessions_dir(self) -> Path:
      # Only use override if in STDIO mode
      if self.session_dir_override and self.mode.upper() == 'STDIO':
          d = Path(self.session_dir_override) / "data"
      else:
          d = self.workspace_dir / "cache" / self.name / "sessions"
      d.mkdir(parents=True, exist_ok=True)
      return d
  
  @property
  def downloads_dir(self) -> Path:
      # Only use override if in STDIO mode
      if self.session_dir_override and self.mode.upper() == 'STDIO':
          d = Path(self.session_dir_override) / "images"
      else:
        d = self.workspace_dir / "cache" / self.name / "downloads"
      d.mkdir(parents=True, exist_ok=True)
      return d