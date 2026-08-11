"""
Ultra-Lightweight Python Media Server for 32-Bit / Single-Core Systems.
Python 3.11.2 Compatible.
Optimized for 720p .mp4 Direct Play with 0% Transcoding Overhead.
"""

import asyncio
import mimetypes
import os
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiofiles
import psutil
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from config import BASE_DIR, HOST, MEDIA_DIR, PORT, STREAM_CHUNK_SIZE, YIELD_EVERY_CHUNKS
from media_scanner import MediaLibrary

app = FastAPI(title="Lightweight 32-Bit Python Media Server", version="1.0.0")

# Enable CORS for local network devices (Smart TVs, tablets, laptops)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Media Library
library = MediaLibrary(media_dir=MEDIA_DIR)

# Track active streaming connections count for live stats
active_streams_count = 0


@app.on_event("startup")
async def startup_event():
    """Load cached media index or trigger background scan on server start."""
    loaded = library.load_cache()
    if not loaded:
        asyncio.create_task(library.refresh_scan())


# Mount static assets
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def get_index():
    """Serve main Single Page Web Interface."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI index.html not found.")
    return FileResponse(str(index_file))


@app.get("/api/stats")
async def get_system_stats():
    """
    Return live CPU and RAM stats of the Python process.
    Allows user to verify ultra-low resource usage (~25MB RAM, ~1% CPU).
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    ram_mb = round(mem_info.rss / (1024 * 1024), 1)
    
    # Process CPU percent (non-blocking call)
    cpu_pct = round(process.cpu_percent(interval=0.0), 1)
    system_cpu = round(psutil.cpu_percent(interval=0.0), 1)

    return {
        "status": "online",
        "process_ram_mb": ram_mb,
        "process_cpu_pct": cpu_pct,
        "system_cpu_pct": system_cpu,
        "total_system_ram_mb": round(psutil.virtual_memory().total / (1024 * 1024), 0),
        "available_system_ram_mb": round(psutil.virtual_memory().available / (1024 * 1024), 0),
        "active_streams": active_streams_count,
        "total_media_count": len(library.items)
    }


@app.get("/api/media")
async def list_media(
    q: Optional[str] = Query(None, description="Search keyword"),
    media_type: Optional[str] = Query(None, description="Filter by 'video' or 'audio'"),
    only_720p: bool = Query(False, description="Filter 720p videos only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(24, ge=1, le=100, description="Items per page")
):
    """Retrieve paginated list of media items with instant search and filtering."""
    import math

    items = library.items

    if media_type:
        items = [i for i in items if i["media_type"] == media_type]

    if only_720p:
        items = [i for i in items if i["is_720p"]]

    if q:
        query_lower = q.lower()
        items = [
            i for i in items
            if query_lower in i["title"].lower() or query_lower in i["filename"].lower()
        ]

    total_filtered = len(items)
    total_pages = math.ceil(total_filtered / limit) if total_filtered > 0 else 1
    
    # Ensure requested page is within valid bounds
    current_page = min(page, total_pages)
    start_idx = (current_page - 1) * limit
    end_idx = start_idx + limit
    page_items = items[start_idx:end_idx]

    return {
        "count": len(page_items),
        "total_items": total_filtered,
        "total_in_library": len(library.items),
        "page": current_page,
        "limit": limit,
        "total_pages": total_pages,
        "items": page_items
    }


@app.post("/api/scan")
async def trigger_scan():
    """Trigger background media directory refresh."""
    asyncio.create_task(library.refresh_scan())
    return {"status": "scanning", "message": "Background library scan started."}


async def range_stream_generator(
    file_path: Path, start: int, end: int, chunk_size: int = STREAM_CHUNK_SIZE
) -> AsyncGenerator[bytes, None]:
    """
    Non-blocking Async Generator for HTTP 206 Byte Range Requests.
    Streams 64 KB chunks asynchronously using aiofiles.
    Yields control to asyncio event loop periodically to prevent event loop starvation
    during background downloads or concurrent playback on single-core CPU.
    """
    global active_streams_count
    active_streams_count += 1
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

                # Cooperative multitasking yield for single core CPU
                if chunk_counter % YIELD_EVERY_CHUNKS == 0:
                    await asyncio.sleep(0)

    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        # Client closed video player or seeked to a new location
        pass
    finally:
        active_streams_count = max(0, active_streams_count - 1)


@app.get("/api/stream/{item_id}")
async def stream_media(item_id: str, request: Request, range_header: Optional[str] = Header(None, alias="Range")):
    """
    Ultra-Optimized 720p HTTP 206 Byte-Range Streaming Engine.
    Enables seeking, fast-forwarding, and direct playback in native HTML5 video/audio tag.
    """
    item = library.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Media item not found.")

    file_path = Path(item["full_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk.")

    file_size = item["size_bytes"]
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or "application/octet-stream"

    # Default full file range if Range header is missing
    start = 0
    end = file_size - 1

    # Parse Range Header (e.g. "bytes=1048576-" or "bytes=0-1048575")
    status_code = 200
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
    }

    if range_header:
        try:
            unit, ranges = range_header.strip().split("=")
            if unit.strip().lower() == "bytes":
                r_start, r_end = ranges.strip().split("-")
                start = int(r_start) if r_start else 0
                end = int(r_end) if r_end else file_size - 1
                
                # Sanity boundary checks
                if start >= file_size:
                    raise HTTPException(
                        status_code=416,
                        detail="Requested Range Not Satisfiable",
                        headers={"Content-Range": f"bytes */{file_size}"}
                    )
                end = min(end, file_size - 1)
                status_code = 206
        except ValueError:
            pass

    content_length = (end - start) + 1
    headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    headers["Content-Length"] = str(content_length)

    return StreamingResponse(
        range_stream_generator(file_path, start, end),
        status_code=status_code,
        headers=headers,
        media_type=content_type
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=False, workers=1)
