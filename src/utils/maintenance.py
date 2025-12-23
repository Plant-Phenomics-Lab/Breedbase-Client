import time
import logging
import sys
from pathlib import Path
from config.type import BrapiServerConfig

def cleanup_old_files(config: BrapiServerConfig, days: int = 30):
    """
    Deletes files in logs, downloads, and sessions directories 
    that are older than the specified number of days.
    """
    limit = time.time() - (days * 86400)
    
    # Directories to clean
    dirs_to_clean = [
        config.log_dir,
        config.downloads_dir,
        config.sessions_dir
    ]
    
    cleaned_count = 0
    
    for directory in dirs_to_clean:
        if not directory.exists():
            continue
            
        for item in directory.rglob('*'):
            if item.is_file():
                try:
                    if item.stat().st_mtime < limit:
                        item.unlink()
                        cleaned_count += 1
                except Exception as e:
                    # Log to stderr to avoid corrupting stdout in stdio mode
                    sys.stderr.write(f"Failed to delete {item}: {e}\n")
    
    if cleaned_count > 0:
        sys.stderr.write(f"Cleanup: Removed {cleaned_count} files older than {days} days.\n")
