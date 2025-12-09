"""
Theater model for cinema halls/screens.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config.database import Base


class Theater(Base):
    """Theater model representing cinema halls/screens."""
    
    __tablename__ = "theaters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    total_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    seats = relationship("Seat", back_populates="theater", cascade="all, delete-orphan")
    showtimes = relationship("Showtime", back_populates="theater", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Theater(id={self.id}, name='{self.name}', seats={self.total_seats})>"
