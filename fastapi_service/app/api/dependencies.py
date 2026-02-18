from fastapi import Request, Depends, HTTPException
from functools import lru_cache
import logging

from ..services.django_service import DjangoService
from ..services.ocr_service import OCRService
from ..services.email_service import EmailService
from ..core.config import Settings, settings

logger = logging.getLogger(__name__)

def get_django_service(request: Request) -> DjangoService:
    """Получение Django сервиса из state"""
    return request.app.state.django_service

def get_ocr_service(request: Request) -> OCRService:
    """Получение OCR сервиса из state"""
    return request.app.state.ocr_service

def get_email_service(request: Request) -> EmailService:
    """Получение Email сервиса из state"""
    return request.app.state.email_service

@lru_cache()
def get_settings() -> Settings:
    """Получение настроек (кэшируется)"""
    return settings

class Services:
    """Контейнер для всех сервисов"""
    def __init__(
        self,
        django_service: DjangoService = Depends(get_django_service),
        ocr_service: OCRService = Depends(get_ocr_service),
        email_service: EmailService = Depends(get_email_service),
        settings: Settings = Depends(get_settings)
    ):
        self.django_service = django_service
        self.ocr_service = ocr_service
        self.email_service = email_service
        self.settings = settings

async def get_services(
    request: Request,
    django: DjangoService = Depends(get_django_service),
    ocr: OCRService = Depends(get_ocr_service),
    email: EmailService = Depends(get_email_service)
) -> Services:
    """Получение всех сервисов сразу"""
    return Services(django, ocr, email)