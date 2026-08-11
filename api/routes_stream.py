"""
API Presentation Layer - Streaming Routes Controller.
Python 3.11.2 Compatible.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from services.library_service import library_service
from services.streaming_service import create_stream_response

router = APIRouter(prefix="/api/stream", tags=["Streaming"])


@router.get("/{item_id}")
async def stream_media(
    item_id: str,
    range_header: Optional[str] = Header(None, alias="Range")
) -> StreamingResponse:
    """Stream media file with HTTP 206 Partial Content Range support."""
    item = library_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Media item not found in library.")

    file_path = Path(item["full_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Media file missing from disk.")

    return create_stream_response(file_path, range_header)
