"""
Shared FastAPI dependencies.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.utils.exceptions import AuthenticationException, AuthorizationException

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    Will be implemented in auth middleware.
    """
    # This is a placeholder - actual implementation will be in middleware/auth.py
    raise NotImplementedError("This dependency will be implemented in auth middleware")


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
            details={"required_role": "admin", "user_role": current_user.role}
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise.
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except AuthenticationException:
        return None
