"""
Reservation API routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from src.config.database import get_db
from src.models.user import User
from src.schemas.reservation import (
    SeatAvailabilityResponse,
    LockSeatsRequest,
    LockSeatsResponse,
    CreateReservationRequest,
    ReservationResponse,
    ReservationWithDetailsResponse,
    ReservationListResponse,
    ReservationSeatResponse,
)
from src.schemas.common import MessageResponse
from src.services.reservation_service import reservation_service
from src.middleware.auth import get_current_user

router = APIRouter(tags=["Reservations"])


@router.get(
    "/showtimes/{showtime_id}/seats",
    response_model=SeatAvailabilityResponse,
    summary="Get seat availability for a showtime"
)
def get_seat_availability(
    showtime_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get real-time seat availability for a specific showtime."""
    availability = reservation_service.get_seat_availability(db, showtime_id)
    return availability


@router.post(
    "/showtimes/{showtime_id}/lock-seats",
    response_model=LockSeatsResponse,
    summary="Temporarily lock seats",
    description="Lock seats for 10 minutes to reserve them during booking process"
)
def lock_seats(
    showtime_id: uuid.UUID,
    lock_request: LockSeatsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Temporarily lock seats before creating reservation."""
    lock_info = reservation_service.lock_seats(
        db,
        current_user,
        showtime_id,
        lock_request.seat_ids
    )
    return LockSeatsResponse(**lock_info)


@router.post(
    "/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reservation"
)
def create_reservation(
    reservation_data: CreateReservationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reservation. Seats must be locked first."""
    reservation = reservation_service.create_reservation(
        db,
        current_user,
        reservation_data.showtime_id,
        reservation_data.seat_ids
    )
    
    # Build response with seat details
    seats = []
    for res_seat in reservation.reservation_seats:
        seat = res_seat.seat
        seats.append(ReservationSeatResponse(
            seat_id=seat.id,
            row_label=seat.row_label,
            seat_number=seat.seat_number,
            seat_label=seat.seat_label,
            seat_type=seat.seat_type
        ))
    
    return ReservationResponse(
        id=reservation.id,
        user_id=reservation.user_id,
        showtime_id=reservation.showtime_id,
        status=reservation.status,
        total_price=reservation.total_price,
        seats=seats,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at
    )


@router.get(
    "/reservations",
    response_model=ReservationListResponse,
    summary="Get user's reservations"
)
def get_user_reservations(
    include_past: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reservations for the authenticated user."""
    reservations = reservation_service.get_user_reservations(
        db,
        current_user,
        include_past=include_past
    )
    
    # Build detailed response
    detailed_reservations = []
    for res in reservations:
        seats = [
            ReservationSeatResponse(
                seat_id=rs.seat.id,
                row_label=rs.seat.row_label,
                seat_number=rs.seat.seat_number,
                seat_label=rs.seat.seat_label,
                seat_type=rs.seat.seat_type
            )
            for rs in res.reservation_seats
        ]
        
        detailed_reservations.append(ReservationWithDetailsResponse(
            id=res.id,
            status=res.status,
            total_price=res.total_price,
            seats=seats,
            showtime={"id": res.showtime.id, "start_time": res.showtime.start_time},
            movie={"id": res.showtime.movie.id, "title": res.showtime.movie.title},
            theater={"id": res.showtime.theater.id, "name": res.showtime.theater.name},
            created_at=res.created_at,
            is_cancellable=res.is_cancellable
        ))
    
    return ReservationListResponse(
        reservations=detailed_reservations,
        total=len(reservations)
    )


@router.delete(
    "/reservations/{reservation_id}",
    response_model=MessageResponse,
    summary="Cancel a reservation"
)
def cancel_reservation(
    reservation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a reservation. Only upcoming reservations can be cancelled."""
    reservation_service.cancel_reservation(db, current_user, reservation_id)
    return MessageResponse(message="Reservation cancelled successfully")
