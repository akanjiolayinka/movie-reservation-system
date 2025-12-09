"""
Admin API routes for analytics and reporting.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import uuid

from src.config.database import get_db
from src.schemas.admin import (
    CapacityReportResponse,
    RevenueReportRequest,
    RevenueReportResponse,
    PopularMoviesResponse,
    PromoteUserRequest,
)
from src.schemas.auth import UserResponse
from src.schemas.common import MessageResponse
from src.services.admin_service import admin_service
from src.middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get(
    "/reports/capacity",
    response_model=CapacityReportResponse,
    summary="Get capacity utilization report"
)
def get_capacity_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[uuid.UUID] = Query(None),
    theater_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Generate capacity utilization report for showtimes."""
    report = admin_service.get_capacity_report(
        db,
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id,
        theater_id=theater_id
    )
    return report


@router.get(
    "/reports/revenue",
    response_model=RevenueReportResponse,
    summary="Get revenue report"
)
def get_revenue_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[uuid.UUID] = Query(None),
    theater_id: Optional[uuid.UUID] = Query(None),
    group_by: str = Query("day", regex="^(day|week|month|movie|theater)$"),
    db: Session = Depends(get_db)
):
    """Generate revenue report with various grouping options."""
    report = admin_service.get_revenue_report(
        db,
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id,
        theater_id=theater_id,
        group_by=group_by
    )
    return report


@router.get(
    "/reports/popular-movies",
    response_model=PopularMoviesResponse,
    summary="Get popular movies report"
)
def get_popular_movies(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get most popular movies by reservations and revenue."""
    report = admin_service.get_popular_movies(
        db,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return report


@router.post(
    "/users/{user_id}/promote",
    response_model=UserResponse,
    summary="Promote or demote user"
)
def promote_user(
    user_id: uuid.UUID,
    promotion_data: PromoteUserRequest,
    db: Session = Depends(get_db)
):
    """Promote user to admin or demote admin to regular user."""
    user = admin_service.promote_user(
        db,
        user_id,
        promotion_data.promote_to_admin
    )
    return UserResponse.model_validate(user)
