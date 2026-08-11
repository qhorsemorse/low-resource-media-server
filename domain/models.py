"""
Domain Layer - Models and Data Schemas.
Python 3.11.2 Compatible.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MediaItem(BaseModel):
    """Domain model representing a single media item."""
    id: str
    title: str
    filename: str
    relative_path: str
    full_path: str
    extension: str
    media_type: str  # 'video' or 'audio'
    size_bytes: int
    size_formatted: str
    mtime: float
    added_date: str
    is_720p: bool


class PaginatedMediaResponse(BaseModel):
    """Domain model for paginated media response."""
    count: int
    total_items: int
    total_in_library: int
    page: int
    limit: int
    total_pages: int
    items: List[MediaItem]


class SystemStatsResponse(BaseModel):
    """Domain model for live system resource metrics."""
    status: str
    process_ram_mb: float
    process_cpu_pct: float
    system_cpu_pct: float
    total_system_ram_mb: float
    available_system_ram_mb: float
    active_streams: int
    total_media_count: int
