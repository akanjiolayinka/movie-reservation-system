"""
Seat model for theater seats.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.config.database import Base


class SeatType(str, enum.Enum):
    """Seat type enumeration."""
    REGULAR = "regular"
    PREMIUM = "premium"
    VIP = "vip"


class Seat(Base):
    """Seat model representing individual seats in a theater."""
    
    __tablename__ = "seats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id", ondelete="CASCADE"), nullable=False)
    row_label = Column(String(10), nullable=False)
    seat_number = Column(Integer, nullable=False)
    seat_type = Column(Enum(SeatType), default=SeatType.REGULAR, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    theater = relationship("Theater", back_populates="seats")
    reservation_seats = relationship("ReservationSeat", back_populates="seat", cascade="all, delete-orphan")
    seat_locks = relationship("SeatLock", back_populates="seat", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('theater_id', 'row_label', 'seat_number', name='uq_theater_row_seat'),
    )
    
    def __repr__(self):
        return f"<Seat(id={self.id}, theater={self.theater_id}, {self.row_label}{self.seat_number})>"
    
    @property
    def seat_label(self) -> str:
        """Get human-readable seat label (e.g., 'A12')."""
        return f"{self.row_label}{self.seat_number}"
