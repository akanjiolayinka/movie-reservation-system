"""
Pydantic schemas for admin endpoints.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid


class CapacityReportRequest(BaseModel):
    """Request schema for capacity report."""
    start_date: Optional[date] = Field(None, description="Start date for report")
    end_date: Optional[date] = Field(None, description="End date for report")
    movie_id: Optional[uuid.UUID] = Field(None, description="Filter by movie")
    theater_id: Optional[uuid.UUID] = Field(None, description="Filter by theater")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-12-01",
                "end_date": "2025-12-31",
                "movie_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class CapacityReportItem(BaseModel):
    """Individual item in capacity report."""
    showtime_id: uuid.UUID
    movie_title: str
    theater_name: str
    start_time: datetime
    total_seats: int
    reserved_seats: int
    available_seats: int
    occupancy_rate: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "showtime_id": "323e4567-e89b-12d3-a456-426614174000",
                "movie_title": "The Matrix",
                "theater_name": "Theater 1",
                "start_time": "2025-12-15T19:00:00Z",
                "total_seats": 100,
                "reserved_seats": 75,
                "available_seats": 25,
                "occupancy_rate": 0.75
            }
        }
    )


class CapacityReportResponse(BaseModel):
    """Response schema for capacity report."""
    report_items: List[CapacityReportItem]
    summary: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_items": [],
                "summary": {
                    "total_showtimes": 50,
                    "total_capacity": 5000,
                    "total_reserved": 3750,
                    "average_occupancy": 0.75
                }
            }
        }
    )


class RevenueReportRequest(BaseModel):
    """Request schema for revenue report."""
    start_date: Optional[date] = Field(None, description="Start date for report")
    end_date: Optional[date] = Field(None, description="End date for report")
    movie_id: Optional[uuid.UUID] = Field(None, description="Filter by movie")
    theater_id: Optional[uuid.UUID] = Field(None, description="Filter by theater")
    group_by: Optional[str] = Field("day", description="Group by: day, week, month, movie, theater")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-12-01",
                "end_date": "2025-12-31",
                "group_by": "movie"
            }
        }
    )


class RevenueReportItem(BaseModel):
    """Individual item in revenue report."""
    label: str
    total_reservations: int
    total_seats_sold: int
    total_revenue: Decimal
    average_ticket_price: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "The Matrix",
                "total_reservations": 150,
                "total_seats_sold": 300,
                "total_revenue": 3750.00,
                "average_ticket_price": 12.50
            }
        }
    )


class RevenueReportResponse(BaseModel):
    """Response schema for revenue report."""
    report_items: List[RevenueReportItem]
    summary: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_items": [],
                "summary": {
                    "total_revenue": 50000.00,
                    "total_reservations": 1000,
                    "total_seats_sold": 2000,
                    "average_ticket_price": 25.00
                }
            }
        }
    )


class PopularMovieItem(BaseModel):
    """Individual item in popular movies report."""
    movie_id: uuid.UUID
    movie_title: str
    genre: str
    total_reservations: int
    total_seats_sold: int
    total_revenue: Decimal
    average_occupancy: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movie_id": "123e4567-e89b-12d3-a456-426614174000",
                "movie_title": "The Matrix",
                "genre": "Sci-Fi",
                "total_reservations": 150,
                "total_seats_sold": 300,
                "total_revenue": 3750.00,
                "average_occupancy": 0.85
            }
        }
    )


class PopularMoviesResponse(BaseModel):
    """Response schema for popular movies report."""
    movies: List[PopularMovieItem]
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movies": [],
                "period_start": "2025-12-01",
                "period_end": "2025-12-31"
            }
        }
    )


class PromoteUserRequest(BaseModel):
    """Request schema for promoting user to admin."""
    promote_to_admin: bool = Field(..., description="True to promote, False to demote")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "promote_to_admin": True
            }
        }
    )
