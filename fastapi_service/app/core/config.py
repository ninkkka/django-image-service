from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field
from typing import Optional

class Settings(BaseSettings):

    APP_NAME: str = "Image OCR Service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    DJANGO_API_URL: str = "http://web:8000/api"
    DJANGO_API_TIMEOUT: int = 30
    
    REDIS_URL: str = "redis://redis:6379/0"
    
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: Optional[str] = None
    EMAIL_HOST_PASSWORD: Optional[str] = None
    DEFAULT_FROM_EMAIL: Optional[EmailStr] = None
    
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()