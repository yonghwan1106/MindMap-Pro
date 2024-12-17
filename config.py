# File: config.py
# Configuration Settings for MindMap Pro

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Application Settings
    APP_NAME = "MindMap Pro"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mindmap_pro.db")
    
    # Redis Settings
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))  # 1 hour
    REFRESH_TOKEN_EXPIRATION = int(os.getenv("REFRESH_TOKEN_EXPIRATION", 2592000))  # 30 days
    
    # Cache Settings
    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File Upload Settings
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {"csv", "json", "xlsx"}

    @staticmethod
    def is_production():
        return Config.ENVIRONMENT == "production"

    @staticmethod
    def is_development():
        return Config.ENVIRONMENT == "development"

    @staticmethod
    def is_testing():
        return Config.ENVIRONMENT == "testing"
