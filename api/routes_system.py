"""
API Presentation Layer - System Operations Controller.
Python 3.11.2 Compatible.
"""

import asyncio
from fastapi import APIRouter
from services.library_service import library_service

router = APIRouter(prefix="/api", tags=["System Operations"])


@router.post("/scan")
async def trigger_scan():
    """Trigger background media library scan."""
    asyncio.create_task(library_service.refresh_scan())
    return {"status": "scanning", "message": "Background library scan started."}
