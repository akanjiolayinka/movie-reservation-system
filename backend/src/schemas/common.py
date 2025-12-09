"""
Common Pydantic schemas used across the application.
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: Dict[str, Any]


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
