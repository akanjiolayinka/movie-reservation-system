"""
Application settings and configuration management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    APP_NAME: str = "Movie Reservation System"
    APP_VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    
    # Seat Lock
    SEAT_LOCK_TTL_MINUTES: int = 10
    SEAT_LOCK_CLEANUP_INTERVAL_SECONDS: int = 60
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_IMAGE_EXTENSIONS into a list."""
        return [ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",")]


# Global settings instance
settings = Settings()
