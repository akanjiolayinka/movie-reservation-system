"""
Movie model for storing movie information.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config.database import Base


class Movie(Base):
    """Movie model for storing movie information."""
    
    __tablename__ = "movies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    poster_url = Column(String(500))
    genre = Column(String(100), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    showtimes = relationship("Showtime", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}', genre='{self.genre}')>"
