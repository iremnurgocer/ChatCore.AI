# -*- coding: utf-8 -*-
"""
Environment Configuration ve Validation

Bu modül environment değişkenlerini yükler ve doğrular.
Pydantic Settings kullanarak type-safe configuration sağlar.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, Literal
import os

class Settings(BaseSettings):
    """Application settings - Environment variables validation"""
    
    # AI Provider
    AI_PROVIDER: Literal["GEMINI", "OPENAI", "AZURE", "OLLAMA", "HUGGINGFACE"] = Field(
        default="GEMINI",
        description="AI sağlayıcı seçimi"
    )
    
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API anahtarı"
    )
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API anahtarı"
    )
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API anahtarı"
    )
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL'i"
    )
    AZURE_OPENAI_DEPLOYMENT: str = Field(
        default="gpt-4o-mini",
        description="Azure OpenAI deployment adı"
    )
    
    # Ollama
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama sunucu adresi"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.2",
        description="Ollama model adı"
    )
    
    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = Field(
        default=None,
        description="Hugging Face API anahtarı"
    )
    HUGGINGFACE_MODEL: str = Field(
        default="distilgpt2",
        description="Hugging Face model adı"
    )
    
    # JWT Secret Key
    SECRET_KEY: str = Field(
        default="supersecret",
        description="JWT imzalama için gizli anahtar"
    )
    
    # Company Name
    COMPANY_NAME: str = Field(
        default="Company1",
        description="Şirket adı"
    )
    
    # Backend URL
    BACKEND_URL: str = Field(
        default="http://127.0.0.1:8000",
        description="Backend API URL'i"
    )
    
    # CORS Origins
    ALLOWED_ORIGINS: str = Field(
        default="*",
        description="CORS izin verilen origin'ler (virgülle ayrılmış)"
    )
    
    # Database (Production için)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Database connection URL (PostgreSQL/MongoDB)"
    )
    
    # Redis (Production için)
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis host adresi"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis port numarası"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis database numarası"
    )
    
    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Log seviyesi"
    )
    LOG_FORMAT: Literal["json", "text"] = Field(
        default="text",
        description="Log formatı (json veya text)"
    )
    
    # Performance
    MAX_REQUEST_SIZE: int = Field(
        default=5000,
        description="Maksimum request boyutu (karakter)"
    )
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Rate limiting aktif mi"
    )
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Production'da SECRET_KEY'in değiştirilmesini zorunlu kıl"""
        if v == "supersecret" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("Production'da SECRET_KEY değiştirilmelidir!")
        return v
    
    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, v: str, info) -> str:
        """AI provider için gerekli API key'lerin kontrolü"""
        provider = v.upper()
        
        if provider == "GEMINI":
            gemini_key = info.data.get("GEMINI_API_KEY")
            if not gemini_key or gemini_key == "your-gemini-api-key-here":
                raise ValueError("GEMINI kullanmak için GEMINI_API_KEY ayarlanmalıdır!")
        
        elif provider == "OPENAI":
            openai_key = info.data.get("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI kullanmak için OPENAI_API_KEY ayarlanmalıdır!")
        
        elif provider == "AZURE":
            azure_key = info.data.get("AZURE_OPENAI_API_KEY")
            azure_endpoint = info.data.get("AZURE_OPENAI_ENDPOINT")
            if not azure_key or not azure_endpoint:
                raise ValueError("AZURE kullanmak için AZURE_OPENAI_API_KEY ve AZURE_OPENAI_ENDPOINT ayarlanmalıdır!")
        
        return provider
    
    @property
    def allowed_origins_list(self) -> list:
        """CORS origins listesi"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Bilinmeyen environment değişkenlerini yoksay

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Global settings instance'ı al"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Backward compatibility için
settings = get_settings()

