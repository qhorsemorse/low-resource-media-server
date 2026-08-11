"""
API Presentation Layer - System Stats Controller.
Python 3.11.2 Compatible.
"""

from fastapi import APIRouter
from core.system import get_system_metrics
from domain.models import SystemStatsResponse
from services.library_service import library_service

router = APIRouter(prefix="/api/stats", tags=["System Stats"])


@router.get("", response_model=SystemStatsResponse)
async def get_stats() -> SystemStatsResponse:
    """Retrieve live CPU, RAM, and stream resource metrics."""
    metrics = get_system_metrics(total_media_count=len(library_service.items))
    return SystemStatsResponse(**metrics)
