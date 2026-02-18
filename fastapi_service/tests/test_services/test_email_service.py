import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.email_service import EmailService
from app.core.exceptions import EmailSendingException

@pytest.mark.asyncio
async def test_send_ocr_result_success():
    """Тест успешной отправки OCR результатов"""
    service = EmailService()
    
    with patch('aiosmtplib.SMTP') as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value.__aenter__.return_value = mock_smtp_instance
        
        # Тестовые данные
        to_email = "test@example.com"
        image_data = {
            'title': 'Test Image',
            'id': '123',
            'uploaded_at': '2026-02-16',
            'size': 1024,
            'width': 800,
            'height': 600,
            'format': 'jpg'
        }
        ocr_text = "Extracted text"
        confidence = 95.5
        
        # Вызов метода
        result = await service.send_ocr_result(to_email, image_data, ocr_text, confidence)
        
        assert result is True
        mock_smtp_instance.connect.assert_called_once()
        if service.username:
            mock_smtp_instance.login.assert_called_once()

@pytest.mark.asyncio
async def test_send_notification_success():
    """Тест успешной отправки уведомления"""
    service = EmailService()
    
    with patch('aiosmtplib.SMTP') as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value.__aenter__.return_value = mock_smtp_instance
        
        result = await service.send_notification(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result is True

@pytest.mark.asyncio
async def test_send_email_smtp_error():
    """Тест ошибки SMTP"""
    service = EmailService()
    
    with patch('aiosmtplib.SMTP') as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value.__aenter__.return_value = mock_smtp_instance
        mock_smtp_instance.send_message.side_effect = Exception("SMTP error")
        
        with pytest.raises(EmailSendingException):
            await service.send_notification(
                to_email="test@example.com",
                subject="Test",
                body="Test"
            )