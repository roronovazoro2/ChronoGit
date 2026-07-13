"""
ChronoGit Backend Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "ChronoGit"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "info"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./chronogit.db",
        description="Database connection URL"
    )
    db_echo: bool = False
    
    # Redis (optional, for caching)
    redis_url: Optional[str] = None
    
    # Git
    git_max_commits: int = Field(
        default=100000,
        description="Maximum number of commits to index"
    )
    git_batch_size: int = 1000
    git_timeout: int = 300  # seconds
    
    # AI
    ai_enabled: bool = True
    ai_model: str = "qwen-coder"
    ai_endpoint: Optional[str] = None  # Local LLM endpoint
    ai_timeout: int = 60
    
    # File system
    data_dir: str = "./data"
    temp_dir: str = "./temp"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Performance
    cache_ttl: int = 300  # seconds
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    # Security
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    api_key: Optional[str] = None
    
    class Config:
        env_prefix = "CHRONOGIT_"
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        return os.getenv("ENVIRONMENT", "development") == "production"
    
    @property
    def use_redis(self) -> bool:
        return self.redis_url is not None


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
