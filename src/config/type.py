from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Optional
import os

@dataclass
class BrapiServerConfig:
  name: str
  base_url: str
  headers: Dict[str, str]
  data_root: Path
  capabilities_override: Optional[Path] = None

  @property
  def csv_dir(self) -> Path:
    d = self.data_root / self.name / "csv"
    d.mkdir(parents=True, exist_ok=True)
    return d

  @property
  def tmp_dir(self) -> Path:
    d = self.data_root / self.name / "tmp"
    d.mkdir(parents=True, exist_ok=True)
    return d

  @property
  def log_dir(self) -> Path:
    d = self.data_root / self.name / "logs"
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