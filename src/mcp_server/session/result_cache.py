# utils/result_cache.py

"""Cache results on MCP server for later retrieval"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import pandas as pd
from datetime import datetime


class ResultCache:
  """
  Manages cached results on the MCP server.
  Used when agents need to save data to avoid context explosion.
  """

  def __init__(self, cache_dir: Path):
    self.cache_dir = cache_dir
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self.metadata_file = cache_dir / 'cache_metadata.json'
    self._load_metadata()

  def _load_metadata(self):
    """Load cache metadata"""
    if self.metadata_file.exists():
      with open(self.metadata_file, 'r') as f:
        self.metadata = json.load(f)
    else:
      self.metadata = {}

  def _save_metadata(self):
    """Save cache metadata"""
    with open(self.metadata_file, 'w') as f:
      json.dump(self.metadata, f, indent=2)

  def save_result(
    self,
    result_id: str,
    data: Any,
    metadata: Optional[Dict] = None,
    format: str = 'csv',
    session_id: Optional[str] = None,
  ) -> Dict[str, Any]:
    """
    Save a result for later retrieval.

    Args:
        result_id: Unique identifier for this result
        data: Data to save (DataFrame, dict, or list)
        metadata: Additional metadata about the result
        format: 'csv', 'json', or 'parquet'

    Returns:
        Info about saved result including size and path
    """
    # Convert data to DataFrame if needed
    if isinstance(data, dict) and 'data' in data:
      df = pd.DataFrame(data['data'])
    elif isinstance(data, list):
      df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
      df = data
    else:
      raise ValueError(f'Unsupported data type: {type(data)}')

    # Save file
    if format == 'csv':
      file_path = self.cache_dir / f'{result_id}.csv'
      df.to_csv(file_path, index=False)
    elif format == 'json':
      file_path = self.cache_dir / f'{result_id}.json'
      df.to_json(file_path, orient='records', indent=2)
    elif format == 'parquet':
      file_path = self.cache_dir / f'{result_id}.parquet'
      df.to_parquet(file_path, index=False)
    else:
      raise ValueError(f'Unsupported format: {format}')

    # Save metadata
    self.metadata[result_id] = {
      'result_id': result_id,
      'session_id': session_id,
      'file_path': str(file_path),
      'format': format,
      'row_count': len(df),
      'column_count': len(df.columns),
      'columns': list(df.columns),
      'size_bytes': file_path.stat().st_size,
      'created_at': datetime.now().isoformat(),
      'metadata': metadata or {},
    }
    self._save_metadata()

    return self.metadata[result_id]

  def get_result_info(self, result_id: str) -> Optional[Dict]:
    """Get metadata about a cached result without loading it"""
    return self.metadata.get(result_id)

  def load_result(
    self,
    result_id: str,
    limit: Optional[int] = None,
    columns: Optional[list[str]] = None,
  ) -> Dict[str, Any]:
    """
    Load a cached result (or part of it).

    Args:
        result_id: ID of cached result
        limit: Maximum rows to return
        columns: Specific columns to return

    Returns:
        Data and metadata
    """
    if result_id not in self.metadata:
      raise ValueError(f'Result {result_id} not found in cache')

    info = self.metadata[result_id]
    file_path = Path(info['file_path'])

    # Load data
    if info['format'] == 'csv':
      df = pd.read_csv(file_path, nrows=limit)
    elif info['format'] == 'json':
      df = pd.read_json(file_path)
      if limit:
        df = df.head(limit)
    elif info['format'] == 'parquet':
      df = pd.read_parquet(file_path)
      if limit:
        df = df.head(limit)

    # Filter columns if requested
    if columns:
      available_cols = [c for c in columns if c in df.columns]
      df = df[available_cols]

    return {
      'data': df.to_dict(orient='records'),
      'metadata': {
        'result_id': result_id,
        'total_rows': info['row_count'],
        'returned_rows': len(df),
        'columns': list(df.columns),
        'truncated': limit is not None and limit < info['row_count'],
      },
    }

  def list_results(self) -> Dict[str, Dict]:
    """List all cached results"""
    return self.metadata

  def delete_result(self, result_id: str) -> bool:
    """Delete a cached result"""
    if result_id not in self.metadata:
      return False

    info = self.metadata[result_id]
    file_path = Path(info['file_path'])

    if file_path.exists():
      file_path.unlink()

    del self.metadata[result_id]
    self._save_metadata()

    return True
