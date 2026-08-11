"""
API Presentation Layer - Media Routes Controller.
Python 3.11.2 Compatible.
"""

from typing import Optional
from fastapi import APIRouter, Query

from domain.models import PaginatedMediaResponse
from services.library_service import library_service

router = APIRouter(prefix="/api/media", tags=["Media"])


@router.get("", response_model=PaginatedMediaResponse)
async def list_media(
    q: Optional[str] = Query(None, description="Search keyword"),
    media_type: Optional[str] = Query(None, description="Filter by 'video' or 'audio'"),
    only_720p: bool = Query(False, description="Filter 720p videos only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(24, ge=1, le=100, description="Items per page")
) -> PaginatedMediaResponse:
    """Retrieve paginated list of media items with instant search and filtering."""
    return library_service.get_paginated_items(
        query=q,
        media_type=media_type,
        only_720p=only_720p,
        page=page,
        limit=limit
    )
