"""
Showtime model for movie screening schedules.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config.database import Base


class Showtime(Base):
    """Showtime model representing movie screening schedules."""
    
    __tablename__ = "showtimes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    movie = relationship("Movie", back_populates="showtimes")
    theater = relationship("Theater", back_populates="showtimes")
    reservations = relationship("Reservation", back_populates="showtime", cascade="all, delete-orphan")
    seat_locks = relationship("SeatLock", back_populates="showtime", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_end_after_start'),
    )
    
    def __repr__(self):
        return f"<Showtime(id={self.id}, movie={self.movie_id}, time={self.start_time})>"
    
    @property
    def is_past(self) -> bool:
        """Check if showtime has already occurred."""
        return self.start_time < datetime.utcnow()
