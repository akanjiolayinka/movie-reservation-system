"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, regular_user):
    """Test registration with existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": regular_user.email,
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, regular_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": regular_user.email,
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data


def test_login_invalid_password(client, regular_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": regular_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user profile."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "role" in data
