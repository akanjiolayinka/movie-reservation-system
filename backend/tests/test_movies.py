"""
Tests for movie management endpoints.
"""
import pytest
from fastapi import status
from datetime import date


@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing."""
    return {
        "title": "Test Movie",
        "description": "A test movie description",
        "genre": "Action",
        "duration_minutes": 120,
        "release_date": "2025-12-31"
    }


def test_create_movie_as_admin(client, admin_headers, sample_movie_data):
    """Test creating a movie as admin."""
    response = client.post(
        "/api/v1/movies",
        json=sample_movie_data,
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sample_movie_data["title"]
    assert "id" in data


def test_create_movie_as_user_forbidden(client, auth_headers, sample_movie_data):
    """Test that regular users cannot create movies."""
    response = client.post(
        "/api/v1/movies",
        json=sample_movie_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_movies(client, admin_headers, sample_movie_data):
    """Test listing movies."""
    # Create a movie first
    client.post("/api/v1/movies", json=sample_movie_data, headers=admin_headers)
    
    # List movies
    response = client.get("/api/v1/movies")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "movies" in data
    assert "total" in data
    assert len(data["movies"]) > 0


def test_get_movie_by_id(client, admin_headers, sample_movie_data):
    """Test getting a specific movie."""
    # Create movie
    create_response = client.post(
        "/api/v1/movies",
        json=sample_movie_data,
        headers=admin_headers
    )
    movie_id = create_response.json()["id"]
    
    # Get movie
    response = client.get(f"/api/v1/movies/{movie_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == movie_id


def test_update_movie(client, admin_headers, sample_movie_data):
    """Test updating a movie."""
    # Create movie
    create_response = client.post(
        "/api/v1/movies",
        json=sample_movie_data,
        headers=admin_headers
    )
    movie_id = create_response.json()["id"]
    
    # Update movie
    response = client.put(
        f"/api/v1/movies/{movie_id}",
        json={"title": "Updated Title"},
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_movie(client, admin_headers, sample_movie_data):
    """Test deleting a movie."""
    # Create movie
    create_response = client.post(
        "/api/v1/movies",
        json=sample_movie_data,
        headers=admin_headers
    )
    movie_id = create_response.json()["id"]
    
    # Delete movie
    response = client.delete(
        f"/api/v1/movies/{movie_id}",
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion
    get_response = client.get(f"/api/v1/movies/{movie_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
