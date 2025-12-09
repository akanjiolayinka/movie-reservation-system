"""Pydantic schemas package."""
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    UserProfileResponse,
)
from src.schemas.movie import (
    MovieCreateRequest,
    MovieUpdateRequest,
    MovieResponse,
    MovieListResponse,
)
from src.schemas.showtime import (
    ShowtimeCreateRequest,
    ShowtimeUpdateRequest,
    ShowtimeResponse,
    ShowtimeWithMovieResponse,
    ShowtimeListResponse,
)
from src.schemas.reservation import (
    SeatResponse,
    SeatAvailabilityResponse,
    LockSeatsRequest,
    LockSeatsResponse,
    CreateReservationRequest,
    ReservationResponse,
    ReservationWithDetailsResponse,
    ReservationListResponse,
)
from src.schemas.admin import (
    CapacityReportRequest,
    CapacityReportResponse,
    RevenueReportRequest,
    RevenueReportResponse,
    PopularMoviesResponse,
    PromoteUserRequest,
)
from src.schemas.common import (
    APIResponse,
    ErrorResponse,
    MessageResponse,
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "UserProfileResponse",
    "MovieCreateRequest",
    "MovieUpdateRequest",
    "MovieResponse",
    "MovieListResponse",
    "ShowtimeCreateRequest",
    "ShowtimeUpdateRequest",
    "ShowtimeResponse",
    "ShowtimeWithMovieResponse",
    "ShowtimeListResponse",
    "SeatResponse",
    "SeatAvailabilityResponse",
    "LockSeatsRequest",
    "LockSeatsResponse",
    "CreateReservationRequest",
    "ReservationResponse",
    "ReservationWithDetailsResponse",
    "ReservationListResponse",
    "CapacityReportRequest",
    "CapacityReportResponse",
    "RevenueReportRequest",
    "RevenueReportResponse",
    "PopularMoviesResponse",
    "PromoteUserRequest",
    "APIResponse",
    "ErrorResponse",
    "MessageResponse",
]
