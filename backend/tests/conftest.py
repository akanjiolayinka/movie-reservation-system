"""
Pytest configuration and fixtures for testing.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.config.database import Base, get_db
from src.models.user import User, UserRole
from src.services.auth_service import auth_service

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db) -> User:
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        password_hash=auth_service.hash_password("admin123"),
        first_name="Admin",
        last_name="Test",
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db) -> User:
    """Create a regular user for testing."""
    user = User(
        email="user@test.com",
        password_hash=auth_service.hash_password("password123"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user) -> str:
    """Get JWT token for admin user."""
    return auth_service.create_access_token(
        user_id=admin_user.id,
        email=admin_user.email,
        role=admin_user.role.value
    )


@pytest.fixture
def user_token(regular_user) -> str:
    """Get JWT token for regular user."""
    return auth_service.create_access_token(
        user_id=regular_user.id,
        email=regular_user.email,
        role=regular_user.role.value
    )


@pytest.fixture
def auth_headers(user_token) -> dict:
    """Get authorization headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Get authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}
