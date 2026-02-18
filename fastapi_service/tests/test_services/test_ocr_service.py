import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ocr_service import OCRService
from app.core.exceptions import OCRProcessingException

@pytest.mark.asyncio
async def test_extract_text_from_url_success():
    """Тест успешного извлечения текста из URL"""
    service = OCRService()
    
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('PIL.Image.open') as mock_image_open, \
         patch('pytesseract.image_to_string') as mock_tesseract:
        
        # Настройка моков
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b'fake-image-content'
        mock_get.return_value = mock_response
        
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_tesseract.return_value = "Extracted text from image"
        
        # Вызов метода
        result = await service.extract_text_from_url("http://test.com/image.jpg")
        
        assert result == "Extracted text from image"
        mock_tesseract.assert_called_once()

@pytest.mark.asyncio
async def test_extract_text_with_confidence_success():
    """Тест извлечения текста с уверенностью"""
    service = OCRService()
    
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('PIL.Image.open') as mock_image_open, \
         patch('pytesseract.image_to_data') as mock_tesseract_data:
        
        # Настройка моков
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b'fake-image-content'
        mock_get.return_value = mock_response
        
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        # Мок данных Tesseract
        mock_tesseract_data.return_value = {
            'text': ['Hello', 'World', '', ''],
            'conf': ['95', '90', '-1', '-1']
        }
        
        # Вызов метода
        result = await service.extract_text_with_confidence("http://test.com/image.jpg")
        
        assert 'text' in result
        assert 'confidence' in result
        assert result['text'] == 'Hello World'

@pytest.mark.asyncio
async def test_extract_text_from_url_http_error():
    """Тест ошибки HTTP при загрузке изображения"""
    service = OCRService()
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        with pytest.raises(OCRProcessingException):
            await service.extract_text_from_url("http://test.com/image.jpg")