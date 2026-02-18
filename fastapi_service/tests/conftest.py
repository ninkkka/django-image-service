import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.main import create_app
from app.core.config import settings
from app.services.django_service import DjangoService
from app.services.ocr_service import OCRService
from app.services.email_service import EmailService

@pytest.fixture
def app():
    """Фикстура для создания приложения"""
    return create_app()

@pytest.fixture
def client(app):
    """Фикстура для тестового клиента"""
    return TestClient(app)

@pytest.fixture
def mock_django_service():
    """Мок для Django сервиса"""
    service = AsyncMock(spec=DjangoService)
    
    # Мок для get_image
    mock_image = MagicMock()
    mock_image.id = uuid4()
    mock_image.title = "Test Image"
    mock_image.image_url = "http://test.com/image.jpg"
    mock_image.uploaded_at = "2026-02-16T10:00:00"
    mock_image.size = 1024
    mock_image.width = 800
    mock_image.height = 600
    mock_image.format = "jpg"
    
    service.get_image.return_value = mock_image
    return service

@pytest.fixture
def mock_ocr_service():
    """Мок для OCR сервиса"""
    service = AsyncMock(spec=OCRService)
    service.extract_text_with_confidence.return_value = {
        'text': 'Sample extracted text',
        'confidence': 95.5
    }
    return service

@pytest.fixture
def mock_email_service():
    """Мок для Email сервиса"""
    service = AsyncMock(spec=EmailService)
    service.send_ocr_result.return_value = True
    return service

@pytest.fixture
def sample_image_id():
    """Фикстура с примером UUID"""
    return uuid4()

@pytest.fixture
def sample_task_id():
    """Фикстура с примером ID задачи"""
    return "550e8400-e29b-41d4-a716-446655440000"