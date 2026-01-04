"""
Application configuration
"""
import os
from typing import List


class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://taskapp:taskapp_password@db:5432/taskapp_db"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") 
        if origin.strip()
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    IS_DEVELOPMENT: bool = ENVIRONMENT == "development"


settings = Settings()
