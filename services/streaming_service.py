"""
Services Layer - Media Streaming Service.
Handles HTTP 206 Partial Content Range Parsing and Async Generator Streaming.
Python 3.11.2 Compatible.
"""

import asyncio
import mimetypes
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional, Tuple

import aiofiles
from fastapi.responses import StreamingResponse

from core.config import STREAM_CHUNK_SIZE, YIELD_EVERY_CHUNKS
from core.system import decrement_active_streams, increment_active_streams
from domain.exceptions import InvalidRangeHeaderException, MediaNotFoundException


async def range_stream_generator(
    file_path: Path, start: int, end: int, chunk_size: int = STREAM_CHUNK_SIZE
) -> AsyncGenerator[bytes, None]:
    """
    Async Generator for streaming 64 KB file chunks.
    Yields control every 512 KB to prevent single-core event loop starvation.
    """
    increment_active_streams()
    chunk_counter = 0

    try:
        async with aiofiles.open(file_path, mode="rb") as f:
            await f.seek(start)
            bytes_to_read = end - start + 1

            while bytes_to_read > 0:
                current_chunk_size = min(chunk_size, bytes_to_read)
                data = await f.read(current_chunk_size)
                if not data:
                    break

                bytes_to_read -= len(data)
                chunk_counter += 1
                yield data

                if chunk_counter % YIELD_EVERY_CHUNKS == 0:
                    await asyncio.sleep(0)

    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        decrement_active_streams()


def parse_range_header(range_header: Optional[str], file_size: int) -> Tuple[int, int, int]:
    """
    Parse HTTP Range header string (e.g. 'bytes=0-1048575').
    Returns (start, end, status_code).
    """
    if not range_header:
        return 0, file_size - 1, 200

    try:
        unit, ranges = range_header.strip().split("=")
        if unit.strip().lower() == "bytes":
            r_start, r_end = ranges.strip().split("-")
            start = int(r_start) if r_start else 0
            end = int(r_end) if r_end else file_size - 1

            if start >= file_size:
                raise InvalidRangeHeaderException(file_size)

            end = min(end, file_size - 1)
            return start, end, 206
    except ValueError:
        pass

    return 0, file_size - 1, 200


def create_stream_response(file_path: Path, range_header: Optional[str] = None) -> StreamingResponse:
    """Build FastAPI StreamingResponse with HTTP 206 Range Headers."""
    if not file_path.exists():
        raise MediaNotFoundException(str(file_path))

    file_size = file_path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or "application/octet-stream"

    start, end, status_code = parse_range_header(range_header, file_size)
    content_length = (end - start) + 1

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Content-Length": str(content_length),
    }

    return StreamingResponse(
        range_stream_generator(file_path, start, end),
        status_code=status_code,
        headers=headers,
        media_type=content_type
    )
