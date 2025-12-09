"""
Authentication middleware for JWT token validation and user retrieval.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.services.auth_service import auth_service
from src.utils.exceptions import AuthenticationException, AuthorizationException

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        AuthenticationException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        # Decode token and extract user ID
        user_id = auth_service.extract_user_id_from_token(token)
        
        # Retrieve user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise AuthenticationException(
                message="User not found",
                details={"user_id": str(user_id)}
            )
        
        return user
        
    except AuthenticationException:
        raise
    except Exception as e:
        raise AuthenticationException(
            message="Authentication failed",
            details={"error": str(e)}
        )


def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Admin user
        
    Raises:
        AuthorizationException: If user is not an admin
    """
    if not current_user.is_admin():
        raise AuthorizationException(
            message="Admin privileges required",
            details={"required_role": "admin", "user_role": current_user.role.value}
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise.
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        Optional[User]: User if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except AuthenticationException:
        return None
