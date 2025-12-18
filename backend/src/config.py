"""Configuration settings for the backend application."""
import os
from typing import Optional


class Settings:
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vision_security.db")
    
    # Camera monitoring settings
    CAMERA_CHECK_INTERVAL_MINUTES: int = int(os.getenv("CAMERA_CHECK_INTERVAL_MINUTES", "5"))
    CAMERA_CHECK_TIMEOUT_SECONDS: int = int(os.getenv("CAMERA_CHECK_TIMEOUT_SECONDS", "1"))
    ENABLE_AUTO_MONITORING: bool = os.getenv("ENABLE_AUTO_MONITORING", "true").lower() == "true"
    
    # Person detection settings
    PERSON_DETECTION_MODEL_PATH: str = os.getenv("PERSON_DETECTION_MODEL_PATH", "/home/cat/backend/src/assert/yolov5.rknn")
    
    # API settings
    API_TITLE: str = "Vision Security Backend"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "Python backend for vision security monitoring system"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # In production, should limit to specific domains
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
