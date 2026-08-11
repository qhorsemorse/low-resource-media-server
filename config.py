"""
Configuration settings optimized for 32-bit Single-Core Python Media Server.
Python 3.11.2 Compatible.
"""

from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Default media folder (can be changed to any directory, e.g. D:/Media or /mnt/storage)
MEDIA_DIR = BASE_DIR / "media"

# Ensure media directory exists
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Server settings
HOST = "0.0.0.0"
PORT = 8000

# Non-blocking Async I/O Chunk size for HTTP Range Requests (64 KB)
# Keeps RAM footprint < 30 MB while giving smooth stream delivery
STREAM_CHUNK_SIZE = 64 * 1024  # 65536 bytes

# Yield control to asyncio event loop after N chunks to prevent event loop starvation
# during background downloads or high disk I/O activity
YIELD_EVERY_CHUNKS = 8  # Yields every 512 KB sent

# Supported media extensions
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".flac", ".ogg", ".wav"}
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

# Library cache file
CACHE_FILE = BASE_DIR / "library_cache.json"
