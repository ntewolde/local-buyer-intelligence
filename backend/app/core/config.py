"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Local Buyer Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+pysqlite:///:memory:"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "test-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Mapbox
    MAPBOX_ACCESS_TOKEN: str = ""
    
    # API Rate Limits
    API_RATE_LIMIT_PER_MINUTE: int = 60
    
    # Feature Flags - Module Gating (PHASE 2)
    # Future work modules can be enabled/disabled via environment variables
    FEATURE_LEAD_FUNNEL_ENABLED: bool = False  # Option 2
    FEATURE_PUBLIC_SIGNALS_ENABLED: bool = False  # Option 3
    FEATURE_CHANNEL_CRM_ENABLED: bool = False  # Option 4
    FEATURE_CAMPAIGNS_ENABLED: bool = False  # Option 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()




