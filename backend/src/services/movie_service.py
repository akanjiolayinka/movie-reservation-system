"""
Movie service for business logic related to movies and showtimes.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from src.models.movie import Movie
from src.models.showtime import Showtime
from src.models.theater import Theater
from src.utils.exceptions import (
    NotFoundException,
    ShowtimeConflictException,
    ValidationException,
)


class MovieService:
    """Service for movie management operations."""
    
    @staticmethod
    def create_movie(db: Session, movie_data: dict) -> Movie:
        """Create a new movie."""
        movie = Movie(**movie_data)
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie
    
    @staticmethod
    def get_movie_by_id(db: Session, movie_id: uuid.UUID) -> Movie:
        """Get movie by ID."""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise NotFoundException(
                message="Movie not found",
                resource="movie",
                details={"movie_id": str(movie_id)}
            )
        return movie
    
    @staticmethod
    def get_movies(
        db: Session,
        genre: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Movie], int]:
        """Get list of movies with optional filtering."""
        query = db.query(Movie)
        
        if genre:
            query = query.filter(Movie.genre.ilike(f"%{genre}%"))
        
        total = query.count()
        movies = query.offset(skip).limit(limit).all()
        
        return movies, total
    
    @staticmethod
    def update_movie(
        db: Session,
        movie_id: uuid.UUID,
        update_data: dict
    ) -> Movie:
        """Update a movie."""
        movie = MovieService.get_movie_by_id(db, movie_id)
        
        for key, value in update_data.items():
            if value is not None and hasattr(movie, key):
                setattr(movie, key, value)
        
        db.commit()
        db.refresh(movie)
        return movie
    
    @staticmethod
    def delete_movie(db: Session, movie_id: uuid.UUID) -> None:
        """Delete a movie."""
        movie = MovieService.get_movie_by_id(db, movie_id)
        db.delete(movie)
        db.commit()
    
    @staticmethod
    def create_showtime(db: Session, showtime_data: dict) -> Showtime:
        """Create a new showtime with conflict validation."""
        # Get movie to calculate end time
        movie = MovieService.get_movie_by_id(db, showtime_data["movie_id"])
        
        # Calculate end time
        start_time = showtime_data["start_time"]
        end_time = start_time + timedelta(minutes=movie.duration_minutes)
        
        # Check for conflicts
        MovieService._check_showtime_conflicts(
            db,
            showtime_data["theater_id"],
            start_time,
            end_time
        )
        
        # Create showtime
        showtime = Showtime(
            **showtime_data,
            end_time=end_time
        )
        db.add(showtime)
        db.commit()
        db.refresh(showtime)
        return showtime
    
    @staticmethod
    def _check_showtime_conflicts(
        db: Session,
        theater_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_showtime_id: Optional[uuid.UUID] = None
    ) -> None:
        """Check for showtime scheduling conflicts."""
        query = db.query(Showtime).filter(
            Showtime.theater_id == theater_id,
            or_(
                # New showtime starts during existing showtime
                and_(
                    Showtime.start_time <= start_time,
                    Showtime.end_time > start_time
                ),
                # New showtime ends during existing showtime
                and_(
                    Showtime.start_time < end_time,
                    Showtime.end_time >= end_time
                ),
                # New showtime completely encompasses existing showtime
                and_(
                    Showtime.start_time >= start_time,
                    Showtime.end_time <= end_time
                )
            )
        )
        
        if exclude_showtime_id:
            query = query.filter(Showtime.id != exclude_showtime_id)
        
        conflicts = query.all()
        
        if conflicts:
            raise ShowtimeConflictException(
                message="Showtime conflicts with existing schedule",
                details={
                    "conflicting_showtimes": [str(s.id) for s in conflicts],
                    "theater_id": str(theater_id),
                    "requested_time": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }
            )
    
    @staticmethod
    def get_showtime_by_id(db: Session, showtime_id: uuid.UUID) -> Showtime:
        """Get showtime by ID."""
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        if not showtime:
            raise NotFoundException(
                message="Showtime not found",
                resource="showtime",
                details={"showtime_id": str(showtime_id)}
            )
        return showtime
    
    @staticmethod
    def get_showtimes_for_movie(
        db: Session,
        movie_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Showtime]:
        """Get showtimes for a specific movie."""
        query = db.query(Showtime).filter(Showtime.movie_id == movie_id)
        
        if start_date:
            query = query.filter(Showtime.start_time >= start_date)
        if end_date:
            query = query.filter(Showtime.start_time <= end_date)
        
        return query.order_by(Showtime.start_time).all()
    
    @staticmethod
    def update_showtime(
        db: Session,
        showtime_id: uuid.UUID,
        update_data: dict
    ) -> Showtime:
        """Update a showtime."""
        showtime = MovieService.get_showtime_by_id(db, showtime_id)
        
        # If updating start_time, validate conflicts
        if "start_time" in update_data:
            movie = showtime.movie
            new_start = update_data["start_time"]
            new_end = new_start + timedelta(minutes=movie.duration_minutes)
            
            MovieService._check_showtime_conflicts(
                db,
                showtime.theater_id,
                new_start,
                new_end,
                exclude_showtime_id=showtime_id
            )
            
            showtime.start_time = new_start
            showtime.end_time = new_end
        
        if "price" in update_data:
            showtime.price = update_data["price"]
        
        db.commit()
        db.refresh(showtime)
        return showtime
    
    @staticmethod
    def delete_showtime(db: Session, showtime_id: uuid.UUID) -> None:
        """Delete a showtime."""
        showtime = MovieService.get_showtime_by_id(db, showtime_id)
        db.delete(showtime)
        db.commit()


# Global instance
movie_service = MovieService()
