"""
SeatLock model for temporary seat holding during reservation process.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config.database import Base
from src.config.settings import settings


class SeatLock(Base):
    """SeatLock model for temporary seat holding to prevent double-booking."""
    
    __tablename__ = "seat_locks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    showtime_id = Column(UUID(as_uuid=True), ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    seat = relationship("Seat", back_populates="seat_locks")
    showtime = relationship("Showtime", back_populates="seat_locks")
    user = relationship("User", back_populates="seat_locks")
    
    # Constraints - one seat can only be locked once per showtime
    __table_args__ = (
        UniqueConstraint('seat_id', 'showtime_id', name='uq_seat_showtime_lock'),
    )
    
    def __repr__(self):
        return f"<SeatLock(id={self.id}, seat={self.seat_id}, expires={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if lock has expired."""
        return self.expires_at < datetime.utcnow()
    
    @classmethod
    def create_expiration_time(cls) -> datetime:
        """Create expiration timestamp based on configured TTL."""
        return datetime.utcnow() + timedelta(minutes=settings.SEAT_LOCK_TTL_MINUTES)
