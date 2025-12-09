"""
Pydantic schemas for movie endpoints.
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime, date
import uuid


class MovieCreateRequest(BaseModel):
    """Request schema for creating a movie."""
    title: str = Field(..., min_length=1, max_length=255, description="Movie title")
    description: Optional[str] = Field(None, description="Movie description")
    genre: str = Field(..., min_length=1, max_length=100, description="Movie genre")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    release_date: Optional[date] = Field(None, description="Release date")
    poster_url: Optional[str] = Field(None, max_length=500, description="Poster image URL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Matrix",
                "description": "A computer hacker learns about the true nature of reality.",
                "genre": "Sci-Fi",
                "duration_minutes": 136,
                "release_date": "1999-03-31",
                "poster_url": "https://example.com/posters/matrix.jpg"
            }
        }
    )


class MovieUpdateRequest(BaseModel):
    """Request schema for updating a movie."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    genre: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(None, gt=0)
    release_date: Optional[date] = None
    poster_url: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Matrix Reloaded",
                "duration_minutes": 138
            }
        }
    )


class MovieResponse(BaseModel):
    """Response schema for movie data."""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    genre: str
    duration_minutes: int
    release_date: Optional[date] = None
    poster_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "The Matrix",
                "description": "A computer hacker learns about the true nature of reality.",
                "genre": "Sci-Fi",
                "duration_minutes": 136,
                "release_date": "1999-03-31",
                "poster_url": "https://example.com/posters/matrix.jpg",
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class MovieListResponse(BaseModel):
    """Response schema for list of movies with pagination."""
    movies: list[MovieResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movies": [],
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        }
    )
