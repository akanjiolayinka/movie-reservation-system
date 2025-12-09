"""
Custom exception classes for the application.
"""
from typing import Any, Optional, Dict
from fastapi import status


class APIException(Exception):
    """Base exception for all API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(APIException):
    """Exception raised for authentication failures."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(APIException):
    """Exception raised for authorization failures."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationException(APIException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            details=details
        )


class NotFoundException(APIException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if resource and not details:
            details = {"resource": resource}
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            details=details
        )


class ConflictException(APIException):
    """Exception raised for business logic conflicts."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            details=details
        )


class BusinessLogicException(APIException):
    """Exception raised for business rule violations."""
    
    def __init__(
        self,
        message: str = "Business logic error",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class SeatAlreadyBookedException(ConflictException):
    """Exception raised when attempting to book already reserved seats."""
    
    def __init__(
        self,
        seat_ids: Optional[list] = None,
        message: str = "One or more seats are already booked"
    ):
        details = {"seat_ids": seat_ids} if seat_ids else {}
        super().__init__(message=message, details=details)


class SeatLockedException(ConflictException):
    """Exception raised when seats are locked by another user."""
    
    def __init__(
        self,
        seat_ids: Optional[list] = None,
        message: str = "One or more seats are currently locked by another user"
    ):
        details = {"seat_ids": seat_ids} if seat_ids else {}
        super().__init__(message=message, details=details)


class ShowtimeConflictException(ConflictException):
    """Exception raised when showtime conflicts with existing schedule."""
    
    def __init__(
        self,
        message: str = "Showtime conflicts with existing schedule",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, details=details)


class ReservationNotCancellableException(BusinessLogicException):
    """Exception raised when trying to cancel non-cancellable reservation."""
    
    def __init__(
        self,
        message: str = "Reservation cannot be cancelled",
        reason: Optional[str] = None
    ):
        details = {"reason": reason} if reason else {}
        super().__init__(message=message, details=details)
