"""
Authentication service for password hashing and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid

from src.config.settings import settings
from src.utils.exceptions import AuthenticationException

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        user_id: uuid.UUID,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User's UUID
            email: User's email
            role: User's role
            expires_delta: Optional custom expiration time
            
        Returns:
            str: JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode: Dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and verify a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict: Token payload
            
        Raises:
            AuthenticationException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise AuthenticationException(
                message="Invalid or expired token",
                details={"error": str(e)}
            )
    
    @staticmethod
    def extract_user_id_from_token(token: str) -> uuid.UUID:
        """
        Extract user ID from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            UUID: User's UUID
            
        Raises:
            AuthenticationException: If token is invalid or missing user ID
        """
        payload = AuthService.decode_token(token)
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise AuthenticationException(
                message="Token missing user information"
            )
        
        try:
            return uuid.UUID(user_id_str)
        except ValueError:
            raise AuthenticationException(
                message="Invalid user ID in token"
            )


# Global instance
auth_service = AuthService()
