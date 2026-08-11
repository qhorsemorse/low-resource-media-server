"""
Media Library Scanner & JSON Cache Manager.
Runs scanning asynchronously to prevent freezing 720p video streams.
Python 3.11.2 Compatible.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import AUDIO_EXTENSIONS, CACHE_FILE, MEDIA_DIR, MEDIA_EXTENSIONS, VIDEO_EXTENSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaScanner")


def format_bytes(size: int) -> str:
    """Format byte size into human readable string (KB, MB, GB)."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def generate_item_id(relative_path: str) -> str:
    """Generate a short unique ID for a media file based on its relative path."""
    return hashlib.md5(relative_path.encode("utf-8")).hexdigest()[:12]


def _scan_directory_sync(target_dir: Path) -> List[Dict[str, Any]]:
    """Synchronous file scanner designed to run in a worker thread."""
    items: List[Dict[str, Any]] = []
    
    if not target_dir.exists():
        logger.warning(f"Target directory does not exist: {target_dir}")
        return items

    for root, _, files in os.walk(target_dir):
        root_path = Path(root)
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext in MEDIA_EXTENSIONS:
                full_path = root_path / filename
                try:
                    stat = full_path.stat()
                    rel_path = str(full_path.relative_to(target_dir)).replace("\\", "/")
                    
                    media_type = "video" if ext in VIDEO_EXTENSIONS else "audio"
                    
                    item = {
                        "id": generate_item_id(rel_path),
                        "title": full_path.stem.replace("_", " ").replace(".", " "),
                        "filename": filename,
                        "relative_path": rel_path,
                        "full_path": str(full_path),
                        "extension": ext,
                        "media_type": media_type,
                        "size_bytes": stat.st_size,
                        "size_formatted": format_bytes(stat.st_size),
                        "mtime": stat.st_mtime,
                        "added_date": time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime)),
                        "is_720p": "720" in filename or "720p" in filename.lower()
                    }
                    items.append(item)
                except (OSError, FileNotFoundError) as e:
                    logger.error(f"Error accessing file {full_path}: {e}")
                    continue

    # Sort items: newest added files first
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items


class MediaLibrary:
    def __init__(self, media_dir: Path = MEDIA_DIR, cache_file: Path = CACHE_FILE):
        self.media_dir = media_dir
        self.cache_file = cache_file
        self.items: List[Dict[str, Any]] = []
        self.items_by_id: Dict[str, Dict[str, Any]] = {}
        self.last_scan_time: float = 0.0

    def load_cache(self) -> bool:
        """Load library items from JSON cache file if present."""
        if not self.cache_file.exists():
            return False
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.items = data.get("items", [])
                self.last_scan_time = data.get("last_scan_time", 0.0)
                self.items_by_id = {item["id"]: item for item in self.items}
                logger.info(f"Loaded {len(self.items)} items from cache.")
                return True
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False

    def save_cache(self) -> None:
        """Save current library items to JSON cache file."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "last_scan_time": self.last_scan_time,
                    "count": len(self.items),
                    "items": self.items
                }, f, indent=2)
            logger.info("Saved library cache.")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    async def refresh_scan(self) -> List[Dict[str, Any]]:
        """Run non-blocking async scan of the media directory in a thread."""
        logger.info("Starting background media scan...")
        # Use asyncio.to_thread to avoid blocking single-core event loop during disk walk
        scanned_items = await asyncio.to_thread(_scan_directory_sync, self.media_dir)
        self.items = scanned_items
        self.items_by_id = {item["id"]: item for item in self.items}
        self.last_scan_time = time.time()
        self.save_cache()
        logger.info(f"Scan complete. Found {len(self.items)} media items.")
        return self.items

    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get media metadata by unique ID."""
        return self.items_by_id.get(item_id)
