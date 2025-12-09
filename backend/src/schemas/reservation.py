"""
Pydantic schemas for reservation endpoints.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

from src.models.reservation import ReservationStatus
from src.models.seat import SeatType


class SeatResponse(BaseModel):
    """Response schema for seat data."""
    id: uuid.UUID
    theater_id: uuid.UUID
    row_label: str
    seat_number: int
    seat_type: SeatType
    seat_label: str
    is_available: Optional[bool] = None
    is_locked: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "423e4567-e89b-12d3-a456-426614174000",
                "theater_id": "223e4567-e89b-12d3-a456-426614174000",
                "row_label": "A",
                "seat_number": 12,
                "seat_type": "regular",
                "seat_label": "A12",
                "is_available": True,
                "is_locked": False
            }
        }
    )


class SeatAvailabilityResponse(BaseModel):
    """Response schema for seat availability."""
    showtime_id: uuid.UUID
    total_seats: int
    available_seats: int
    seats: List[SeatResponse]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "showtime_id": "323e4567-e89b-12d3-a456-426614174000",
                "total_seats": 100,
                "available_seats": 75,
                "seats": []
            }
        }
    )


class LockSeatsRequest(BaseModel):
    """Request schema for locking seats temporarily."""
    seat_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of seat IDs to lock")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "seat_ids": [
                    "423e4567-e89b-12d3-a456-426614174000",
                    "423e4567-e89b-12d3-a456-426614174001"
                ]
            }
        }
    )


class LockSeatsResponse(BaseModel):
    """Response schema for seat lock."""
    locked_seat_ids: List[uuid.UUID]
    expires_at: datetime
    lock_duration_minutes: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "locked_seat_ids": [
                    "423e4567-e89b-12d3-a456-426614174000",
                    "423e4567-e89b-12d3-a456-426614174001"
                ],
                "expires_at": "2025-12-09T10:10:00Z",
                "lock_duration_minutes": 10
            }
        }
    )


class CreateReservationRequest(BaseModel):
    """Request schema for creating a reservation."""
    showtime_id: uuid.UUID = Field(..., description="Showtime ID")
    seat_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of seat IDs to reserve")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "showtime_id": "323e4567-e89b-12d3-a456-426614174000",
                "seat_ids": [
                    "423e4567-e89b-12d3-a456-426614174000",
                    "423e4567-e89b-12d3-a456-426614174001"
                ]
            }
        }
    )


class ReservationSeatResponse(BaseModel):
    """Response schema for reservation seat."""
    seat_id: uuid.UUID
    row_label: str
    seat_number: int
    seat_label: str
    seat_type: SeatType
    
    model_config = ConfigDict(from_attributes=True)


class ReservationResponse(BaseModel):
    """Response schema for reservation data."""
    id: uuid.UUID
    user_id: uuid.UUID
    showtime_id: uuid.UUID
    status: ReservationStatus
    total_price: Decimal
    seats: List[ReservationSeatResponse]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "523e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "showtime_id": "323e4567-e89b-12d3-a456-426614174000",
                "status": "confirmed",
                "total_price": 25.00,
                "seats": [],
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class ReservationWithDetailsResponse(BaseModel):
    """Response schema for reservation with full details."""
    id: uuid.UUID
    status: ReservationStatus
    total_price: Decimal
    seats: List[ReservationSeatResponse]
    showtime: dict  # ShowtimeResponse
    movie: dict  # MovieResponse
    theater: dict  # TheaterResponse
    created_at: datetime
    is_cancellable: bool
    
    model_config = ConfigDict(from_attributes=True)


class ReservationListResponse(BaseModel):
    """Response schema for list of reservations."""
    reservations: List[ReservationWithDetailsResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reservations": [],
                "total": 10
            }
        }
    )
