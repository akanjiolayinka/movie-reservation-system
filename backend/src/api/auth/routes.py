"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
)
from src.services.auth_service import auth_service
from src.middleware.auth import get_current_user
from src.utils.exceptions import AuthenticationException, ValidationException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return access token"
)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValidationException(
            message="Email already registered",
            details={"email": user_data.email}
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=auth_service.hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate access token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return TokenResponse(access_token=access_token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access token"
)
def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise AuthenticationException(
            message="Invalid email or password"
        )
    
    # Verify password
    if not auth_service.verify_password(credentials.password, user.password_hash):
        raise AuthenticationException(
            message="Invalid email or password"
        )
    
    # Generate access token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user's profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.get_full_name(),
        role=current_user.role,
        is_admin=current_user.is_admin(),
        created_at=current_user.created_at
    )
