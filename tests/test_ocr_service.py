import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from images.infrastructure.services import TesseractOCRService, DjangoEmailService
from images.tasks import extract_text_from_image, send_analysis_notification

@pytest.mark.django_db
class TestOCRService:
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.threshold')
    @patch('pytesseract.image_to_string')
    def test_extract_text_success(self, mock_tesseract, mock_threshold, mock_cvt, mock_imread):
        mock_imread.return_value = MagicMock()
        mock_cvt.return_value = MagicMock()
        mock_threshold.return_value = (None, MagicMock())
        mock_tesseract.return_value = "Extracted text"
        
        service = TesseractOCRService()
        
        result = service.extract_text("/fake/path/image.jpg")
        
        assert result == "Extracted text"
        mock_tesseract.assert_called_once()
    
    @patch('os.path.exists')
    def test_extract_text_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        service = TesseractOCRService()
        
        with pytest.raises(FileNotFoundError):
            service.extract_text("/fake/path/image.jpg")

@pytest.mark.django_db
class TestEmailService:
    
    @patch('django.core.mail.send_mail')
    def test_send_notification_success(self, mock_send_mail):
        mock_send_mail.return_value = 1
        service = DjangoEmailService()
        
        result = service.send_notification(
            to_email="test@example.com",
            image_title="Test Image",
            extracted_text="Some text"
        )
        
        assert result is True
        mock_send_mail.assert_called_once()
    
    @patch('django.core.mail.send_mail')
    def test_send_notification_failure(self, mock_send_mail):
        mock_send_mail.side_effect = Exception("SMTP error")
        service = DjangoEmailService()
        
        result = service.send_notification(
            to_email="test@example.com",
            image_title="Test Image",
            extracted_text="Some text"
        )
        
        assert result is False