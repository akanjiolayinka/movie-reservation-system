"""
Pydantic schemas for showtime endpoints.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import uuid


class ShowtimeCreateRequest(BaseModel):
    """Request schema for creating a showtime."""
    movie_id: uuid.UUID = Field(..., description="Movie ID")
    theater_id: uuid.UUID = Field(..., description="Theater ID")
    start_time: datetime = Field(..., description="Showtime start time")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Ticket price")
    
    @field_validator('start_time')
    @classmethod
    def validate_future_time(cls, v: datetime) -> datetime:
        """Ensure start time is in the future."""
        if v < datetime.utcnow():
            raise ValueError("Start time must be in the future")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movie_id": "123e4567-e89b-12d3-a456-426614174000",
                "theater_id": "223e4567-e89b-12d3-a456-426614174000",
                "start_time": "2025-12-15T19:00:00Z",
                "price": 12.50
            }
        }
    )


class ShowtimeUpdateRequest(BaseModel):
    """Request schema for updating a showtime."""
    start_time: Optional[datetime] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    
    @field_validator('start_time')
    @classmethod
    def validate_future_time(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure start time is in the future if provided."""
        if v and v < datetime.utcnow():
            raise ValueError("Start time must be in the future")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_time": "2025-12-15T20:00:00Z",
                "price": 15.00
            }
        }
    )


class ShowtimeResponse(BaseModel):
    """Response schema for showtime data."""
    id: uuid.UUID
    movie_id: uuid.UUID
    theater_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    price: Decimal
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "323e4567-e89b-12d3-a456-426614174000",
                "movie_id": "123e4567-e89b-12d3-a456-426614174000",
                "theater_id": "223e4567-e89b-12d3-a456-426614174000",
                "start_time": "2025-12-15T19:00:00Z",
                "end_time": "2025-12-15T21:16:00Z",
                "price": 12.50,
                "created_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class ShowtimeWithMovieResponse(BaseModel):
    """Response schema for showtime with movie details."""
    id: uuid.UUID
    start_time: datetime
    end_time: datetime
    price: Decimal
    movie: dict  # MovieResponse
    theater: dict  # TheaterResponse
    available_seats: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ShowtimeListResponse(BaseModel):
    """Response schema for list of showtimes."""
    showtimes: list[ShowtimeResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "showtimes": [],
                "total": 50
            }
        }
    )
