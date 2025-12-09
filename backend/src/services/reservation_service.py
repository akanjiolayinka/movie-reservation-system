"""
Reservation service for seat booking with concurrency control.
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from decimal import Decimal
import uuid

from src.models.seat import Seat
from src.models.showtime import Showtime
from src.models.reservation import Reservation, ReservationSeat, ReservationStatus
from src.models.seat_lock import SeatLock
from src.models.user import User
from src.utils.exceptions import (
    NotFoundException,
    SeatAlreadyBookedException,
    SeatLockedException,
    BusinessLogicException,
    ReservationNotCancellableException,
)


class ReservationService:
    """Service for reservation and seat locking operations."""
    
    @staticmethod
    def get_seat_availability(
        db: Session,
        showtime_id: uuid.UUID
    ) -> Dict:
        """
        Get seat availability for a showtime.
        
        Returns all seats with their availability status.
        """
        # Verify showtime exists
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        if not showtime:
            raise NotFoundException(
                message="Showtime not found",
                resource="showtime"
            )
        
        # Get all seats for the theater
        seats = db.query(Seat).filter(
            Seat.theater_id == showtime.theater_id
        ).order_by(Seat.row_label, Seat.seat_number).all()
        
        # Get reserved seat IDs for this showtime
        reserved_seats = db.query(ReservationSeat.seat_id).join(
            Reservation
        ).filter(
            Reservation.showtime_id == showtime_id,
            Reservation.status == ReservationStatus.CONFIRMED
        ).all()
        reserved_seat_ids = {seat_id for (seat_id,) in reserved_seats}
        
        # Get locked seat IDs for this showtime (not expired)
        locked_seats = db.query(SeatLock.seat_id).filter(
            SeatLock.showtime_id == showtime_id,
            SeatLock.expires_at > datetime.utcnow()
        ).all()
        locked_seat_ids = {seat_id for (seat_id,) in locked_seats}
        
        # Build seat availability list
        seat_list = []
        available_count = 0
        
        for seat in seats:
            is_reserved = seat.id in reserved_seat_ids
            is_locked = seat.id in locked_seat_ids
            is_available = not is_reserved and not is_locked
            
            if is_available:
                available_count += 1
            
            seat_list.append({
                "id": seat.id,
                "theater_id": seat.theater_id,
                "row_label": seat.row_label,
                "seat_number": seat.seat_number,
                "seat_type": seat.seat_type,
                "seat_label": seat.seat_label,
                "is_available": is_available,
                "is_locked": is_locked
            })
        
        return {
            "showtime_id": showtime_id,
            "total_seats": len(seats),
            "available_seats": available_count,
            "seats": seat_list
        }
    
    @staticmethod
    def lock_seats(
        db: Session,
        user: User,
        showtime_id: uuid.UUID,
        seat_ids: List[uuid.UUID]
    ) -> Dict:
        """
        Temporarily lock seats for a user.
        
        Uses pessimistic locking to prevent race conditions.
        """
        # Verify showtime exists and is in the future
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        if not showtime:
            raise NotFoundException(message="Showtime not found", resource="showtime")
        
        if showtime.is_past:
            raise BusinessLogicException(
                message="Cannot lock seats for past showtimes"
            )
        
        # Verify all seats exist and belong to the showtime's theater
        seats = db.query(Seat).filter(
            Seat.id.in_(seat_ids),
            Seat.theater_id == showtime.theater_id
        ).with_for_update(nowait=False).all()
        
        if len(seats) != len(seat_ids):
            found_ids = {s.id for s in seats}
            missing_ids = set(seat_ids) - found_ids
            raise NotFoundException(
                message="Some seats not found or invalid for this showtime",
                details={"missing_seat_ids": [str(sid) for sid in missing_ids]}
            )
        
        # Check if seats are already reserved
        reserved_seats = db.query(ReservationSeat.seat_id).join(
            Reservation
        ).filter(
            Reservation.showtime_id == showtime_id,
            Reservation.status == ReservationStatus.CONFIRMED,
            ReservationSeat.seat_id.in_(seat_ids)
        ).all()
        
        if reserved_seats:
            reserved_ids = [str(sid) for (sid,) in reserved_seats]
            raise SeatAlreadyBookedException(
                seat_ids=reserved_ids,
                message="Some seats are already booked"
            )
        
        # Check if seats are locked by another user
        existing_locks = db.query(SeatLock).filter(
            SeatLock.showtime_id == showtime_id,
            SeatLock.seat_id.in_(seat_ids),
            SeatLock.expires_at > datetime.utcnow(),
            SeatLock.user_id != user.id
        ).all()
        
        if existing_locks:
            locked_ids = [str(lock.seat_id) for lock in existing_locks]
            raise SeatLockedException(
                seat_ids=locked_ids,
                message="Some seats are currently locked by another user"
            )
        
        # Remove any expired locks for these seats
        db.query(SeatLock).filter(
            SeatLock.showtime_id == showtime_id,
            SeatLock.seat_id.in_(seat_ids),
            SeatLock.user_id == user.id
        ).delete(synchronize_session=False)
        
        # Create new locks
        expires_at = SeatLock.create_expiration_time()
        locks = []
        
        for seat_id in seat_ids:
            lock = SeatLock(
                seat_id=seat_id,
                showtime_id=showtime_id,
                user_id=user.id,
                expires_at=expires_at
            )
            locks.append(lock)
            db.add(lock)
        
        db.commit()
        
        return {
            "locked_seat_ids": seat_ids,
            "expires_at": expires_at,
            "lock_duration_minutes": (expires_at - datetime.utcnow()).seconds // 60
        }
    
    @staticmethod
    def create_reservation(
        db: Session,
        user: User,
        showtime_id: uuid.UUID,
        seat_ids: List[uuid.UUID]
    ) -> Reservation:
        """
        Create a reservation with atomic seat booking.
        
        Verifies seat locks and prevents double-booking.
        """
        # Verify showtime exists
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        if not showtime:
            raise NotFoundException(message="Showtime not found", resource="showtime")
        
        if showtime.is_past:
            raise BusinessLogicException(
                message="Cannot create reservation for past showtimes"
            )
        
        # Verify user has valid locks on all seats
        locks = db.query(SeatLock).filter(
            SeatLock.user_id == user.id,
            SeatLock.showtime_id == showtime_id,
            SeatLock.seat_id.in_(seat_ids),
            SeatLock.expires_at > datetime.utcnow()
        ).with_for_update(nowait=False).all()
        
        if len(locks) != len(seat_ids):
            raise BusinessLogicException(
                message="Must lock seats before creating reservation",
                details={"required_locks": len(seat_ids), "found_locks": len(locks)}
            )
        
        # Double-check seats aren't already reserved (race condition protection)
        reserved_check = db.query(ReservationSeat.seat_id).join(
            Reservation
        ).filter(
            Reservation.showtime_id == showtime_id,
            Reservation.status == ReservationStatus.CONFIRMED,
            ReservationSeat.seat_id.in_(seat_ids)
        ).first()
        
        if reserved_check:
            raise SeatAlreadyBookedException(
                message="Seats were booked by someone else"
            )
        
        # Calculate total price
        total_price = Decimal(str(showtime.price)) * len(seat_ids)
        
        # Create reservation
        reservation = Reservation(
            user_id=user.id,
            showtime_id=showtime_id,
            status=ReservationStatus.CONFIRMED,
            total_price=total_price
        )
        db.add(reservation)
        db.flush()  # Get reservation ID
        
        # Link seats to reservation
        for seat_id in seat_ids:
            res_seat = ReservationSeat(
                reservation_id=reservation.id,
                seat_id=seat_id
            )
            db.add(res_seat)
        
        # Delete locks (no longer needed)
        db.query(SeatLock).filter(
            SeatLock.user_id == user.id,
            SeatLock.showtime_id == showtime_id,
            SeatLock.seat_id.in_(seat_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        db.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def get_user_reservations(
        db: Session,
        user: User,
        include_past: bool = False
    ) -> List[Reservation]:
        """Get all reservations for a user."""
        query = db.query(Reservation).filter(
            Reservation.user_id == user.id
        )
        
        if not include_past:
            query = query.join(Showtime).filter(
                Showtime.start_time >= datetime.utcnow()
            )
        
        return query.order_by(Reservation.created_at.desc()).all()
    
    @staticmethod
    def get_reservation_by_id(
        db: Session,
        reservation_id: uuid.UUID,
        user: Optional[User] = None
    ) -> Reservation:
        """Get reservation by ID, optionally verifying ownership."""
        query = db.query(Reservation).filter(Reservation.id == reservation_id)
        
        if user:
            query = query.filter(Reservation.user_id == user.id)
        
        reservation = query.first()
        
        if not reservation:
            raise NotFoundException(
                message="Reservation not found",
                resource="reservation"
            )
        
        return reservation
    
    @staticmethod
    def cancel_reservation(
        db: Session,
        user: User,
        reservation_id: uuid.UUID
    ) -> Reservation:
        """Cancel a reservation."""
        reservation = ReservationService.get_reservation_by_id(
            db, reservation_id, user
        )
        
        if not reservation.is_cancellable:
            reason = "Showtime has already started or passed" if reservation.showtime.is_past else "Already cancelled"
            raise ReservationNotCancellableException(
                message="Reservation cannot be cancelled",
                reason=reason
            )
        
        reservation.status = ReservationStatus.CANCELLED
        db.commit()
        db.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def cleanup_expired_locks(db: Session) -> int:
        """
        Clean up expired seat locks.
        
        Called periodically by background task.
        
        Returns:
            int: Number of locks deleted
        """
        deleted = db.query(SeatLock).filter(
            SeatLock.expires_at <= datetime.utcnow()
        ).delete(synchronize_session=False)
        
        db.commit()
        return deleted


# Global instance
reservation_service = ReservationService()
