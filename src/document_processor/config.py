"""
Configuration Management
Centralized configuration for the document processor
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY", description="Gemini API key")
    gemini_model: str = Field("gemini-2.0-flash-exp", env="GEMINI_MODEL", description="Gemini model to use")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST", description="Server host")
    port: int = Field(8000, env="PORT", description="Server port")
    debug: bool = Field(False, env="DEBUG", description="Debug mode")
    
    # Processing Configuration
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE", description="Max file size in bytes (10MB)")
    supported_formats: list[str] = Field(["image/jpeg", "image/png", "image/bmp", "image/tiff"], description="Supported image formats")
    processing_timeout: int = Field(60, env="PROCESSING_TIMEOUT", description="Processing timeout in seconds")
    
    # Validation Configuration
    min_confidence_threshold: float = Field(0.5, env="MIN_CONFIDENCE_THRESHOLD", description="Minimum confidence for valid extraction")
    enable_validation: bool = Field(True, env="ENABLE_VALIDATION", description="Enable data validation")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings