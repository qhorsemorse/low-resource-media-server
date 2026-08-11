"""
Backwards Compatibility Config Re-exporter.
Imports all settings from core.config module.
"""

from core.config import (
    AUDIO_EXTENSIONS,
    BASE_DIR,
    CACHE_FILE,
    HOST,
    MEDIA_DIR,
    MEDIA_EXTENSIONS,
    PORT,
    STATIC_DIR,
    STREAM_CHUNK_SIZE,
    VIDEO_EXTENSIONS,
    YIELD_EVERY_CHUNKS,
)
