import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from fastapi import status

def test_health_check(client):
    """Тест проверки здоровья"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

@pytest.mark.asyncio
async def test_analyze_doc_success(client, mock_django_service, mock_ocr_service, mock_email_service, sample_image_id):
    """Тест успешного запуска OCR"""
    with patch('app.api.routes.process_ocr_task') as mock_task:
        # Настройка мока задачи
        mock_async_result = MagicMock()
        mock_async_result.id = "test-task-id-123"
        mock_task.delay.return_value = mock_async_result
        
        # Подмена сервисов в state
        client.app.state.django_service = mock_django_service
        client.app.state.ocr_service = mock_ocr_service
        client.app.state.email_service = mock_email_service
        
        # Отправка запроса
        response = client.post(
            "/api/v1/analyze_doc",
            json={
                "image_id": str(sample_image_id),
                "send_email": True,
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == "test-task-id-123"
        assert data["status"] == "processing"

@pytest.mark.asyncio
async def test_analyze_doc_image_not_found(client, mock_django_service, sample_image_id):
    """Тест, когда изображение не найдено"""
    # Настройка мока на ошибку
    from app.core.exceptions import ImageNotFoundException
    mock_django_service.get_image.side_effect = ImageNotFoundException(str(sample_image_id))
    
    client.app.state.django_service = mock_django_service
    
    response = client.post(
        "/api/v1/analyze_doc",
        json={
            "image_id": str(sample_image_id),
            "send_email": True
        }
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "не найдено" in response.json()["detail"]

def test_send_message_to_email_success(client, mock_email_service):
    """Тест успешной отправки email"""
    client.app.state.email_service = mock_email_service
    
    response = client.post(
        "/api/v1/send_message_to_email",
        json={
            "to_email": "test@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True

def test_get_task_status_pending(client):
    """Тест получения статуса задачи"""
    with patch('celery.result.AsyncResult') as mock_async_result:
        mock_result = MagicMock()
        mock_result.state = 'PENDING'
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/v1/task_status/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["state"] == 'PENDING'