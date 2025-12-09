"""
Reservation models for seat bookings.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Enum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.config.database import Base


class ReservationStatus(str, enum.Enum):
    """Reservation status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base):
    """Reservation model for seat bookings."""
    
    __tablename__ = "reservations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    showtime_id = Column(UUID(as_uuid=True), ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.CONFIRMED, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reservations")
    showtime = relationship("Showtime", back_populates="reservations")
    reservation_seats = relationship("ReservationSeat", back_populates="reservation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, user={self.user_id}, status='{self.status}')>"
    
    @property
    def is_cancellable(self) -> bool:
        """Check if reservation can be cancelled."""
        return (
            self.status == ReservationStatus.CONFIRMED and
            self.showtime and
            not self.showtime.is_past
        )


class ReservationSeat(Base):
    """Association table for many-to-many relationship between reservations and seats."""
    
    __tablename__ = "reservation_seats"
    
    reservation_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("reservations.id", ondelete="CASCADE"), 
        primary_key=True
    )
    seat_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("seats.id", ondelete="CASCADE"), 
        primary_key=True
    )
    
    # Relationships
    reservation = relationship("Reservation", back_populates="reservation_seats")
    seat = relationship("Seat", back_populates="reservation_seats")
    
    def __repr__(self):
        return f"<ReservationSeat(reservation={self.reservation_id}, seat={self.seat_id})>"
