"""
Core Configuration module for 32-Bit Python Media Server.
Python 3.11.2 Compatible.
"""

import os
from pathlib import Path

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Default media folder
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Server network settings
HOST = "0.0.0.0"
PORT = 8000

# Non-blocking Async I/O Chunk size for HTTP Range Requests (64 KB)
STREAM_CHUNK_SIZE = 64 * 1024  # 65536 bytes

# Yield control to asyncio event loop every N chunks (512 KB)
YIELD_EVERY_CHUNKS = 8

# Supported media extensions
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".flac", ".ogg", ".wav"}
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

# Library cache file path
CACHE_FILE = BASE_DIR / "library_cache.json"

# Static directory path
STATIC_DIR = BASE_DIR / "static"
