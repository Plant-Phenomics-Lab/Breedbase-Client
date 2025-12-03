from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional
import os

@dataclass
class BrapiServerConfig:
  name: str
  base_url: str
  capabilities_override: Optional[Path] = None

  @property
  def workspace_dir(self) -> Path:
    d = Path(__file__).parent.parent.parent
    return d
  
  @property
  def log_dir(self) -> Path:
    d = self.workspace_dir / self.name / "logs" 
    d.mkdir(parents=True, exist_ok=True)
    return d

  @property
  def downloads_dir(self) -> Path:
    d = self.workspace_dir / self.name / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d
  
  @property
  def sessions_dir(self) -> Path:
    d = self.workspace_dir / self.name / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d

  # TODO :: Using same keys for username and password for backward
  # compatibility, implement better username & password loading
  @property
  def username(self) -> str:
    load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
    return os.getenv("SWEETPOTATOBASE_USERNAME")

  @property
  def password(self) -> str:
    load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
    return os.getenv("SWEETPOTATOBASE_PASSWORD")
  
  @property
  def port(self)-> Optional[int]:
    load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
    port = os.getenv("PORT")
    return int(port) if port is not None else 8000