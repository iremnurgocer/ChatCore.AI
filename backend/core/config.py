# -*- coding: utf-8 -*-
"""
Module: Core Configuration
Description: Environment variable management using Pydantic Settings with validation.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, Literal, List
import os


class Settings(BaseSettings):
    """Application settings with environment variable validation"""
    
    # Application
    APP_NAME: str = Field(default="ChatCore.AI Enterprise API", description="Application name")
    COMPANY_NAME: str = Field(default="Company1", description="Company name")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment"
    )
    
    # AI Provider
    AI_PROVIDER: Literal["GEMINI", "OPENAI", "AZURE", "OLLAMA", "HUGGINGFACE"] = Field(
        default="GEMINI", description="AI provider"
    )
    
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API key")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    AZURE_OPENAI_DEPLOYMENT: str = Field(default="gpt-4o-mini", description="Azure deployment name")
    
    # Ollama
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama base URL")
    OLLAMA_MODEL: str = Field(default="llama3.2", description="Ollama model name")
    
    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, description="Hugging Face API key")
    HUGGINGFACE_MODEL: str = Field(default="distilgpt2", description="Hugging Face model")
    
    # Security
    SECRET_KEY: str = Field(default="supersecret", description="JWT secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Access token expiry (minutes)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="Refresh token expiry (days)")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # Database
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (e.g., postgresql://user:pass@localhost/dbname)"
    )
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Log level"
    )
    LOG_FORMAT: Literal["json", "text"] = Field(default="json", description="Log format")
    
    # Performance
    MAX_REQUEST_SIZE: int = Field(default=5000, description="Max request size (chars)")
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window (seconds)")
    
    # FAISS
    FAISS_INDEX_PATH: str = Field(
        default="./data/faiss_index",
        description="Path to FAISS index directory"
    )
    
    # Celery (optional)
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend")
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Enforce strong secret key in production"""
        if v == "supersecret" and info.data.get("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be changed in production!")
        return v
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Prevent wildcard '*' in production"""
        if v == "*" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("Wildcard '*' not allowed in production. Specify exact origins.")
        return v
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def database_url_sync(self) -> Optional[str]:
        """Get synchronous database URL"""
        if not self.DATABASE_URL:
            return None
        
        url = self.DATABASE_URL
        # Remove any existing driver prefix
        if "+asyncpg" in url:
            url = url.replace("postgresql+asyncpg://", "postgresql://")
        elif "+psycopg2" in url:
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        
        # Add psycopg2 driver
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        return url
    
    @property
    def database_url_async(self) -> Optional[str]:
        """Get async database URL"""
        if not self.DATABASE_URL:
            return None
        
        url = self.DATABASE_URL
        # Remove any existing driver prefix
        if "+psycopg2" in url:
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        elif "+asyncpg" in url:
            url = url.replace("postgresql+asyncpg://", "postgresql://")
        
        # Add asyncpg driver
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Backward compatibility
settings = get_settings()

