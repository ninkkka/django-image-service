import pytesseract
from PIL import Image
import httpx
import io
import logging
from typing import Optional, Dict
from ..core.config import settings
from ..core.exceptions import OCRProcessingException

logger = logging.getLogger(__name__)

class OCRService:
    """Сервис для распознавания текста на изображениях"""
    
    def __init__(self, tesseract_cmd: str = settings.TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        logger.info(f"OCR Service initialized with tesseract: {tesseract_cmd}")
    
    async def extract_text_from_url(self, image_url: str) -> str:
        """Извлечение текста из изображения по URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                text = await self._extract_text_from_image(image)
                return text
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            raise OCRProcessingException(f"OCR processing failed: {str(e)}")
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """Внутренний метод для извлечения текста"""
        try:
            custom_config = r'--oem 3 --psm 6 -l rus+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            return ' '.join(text.split())
        except Exception as e:
            logger.error(f"Tesseract processing error: {str(e)}")
            raise OCRProcessingException(f"Tesseract failed: {str(e)}")
    
    async def extract_text_with_confidence(self, image_url: str) -> Dict:
        """Извлечение текста с уверенностью распознавания"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                text_parts = []
                confidences = []
                
                for i, text in enumerate(data['text']):
                    if text.strip():
                        text_parts.append(text)
                        try:
                            conf = int(data['conf'][i])
                            if conf > 0:
                                confidences.append(conf)
                        except (ValueError, TypeError):
                            pass
                
                full_text = ' '.join(text_parts)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return {
                    'text': full_text,
                    'confidence': round(avg_confidence, 2)
                }
        except Exception as e:
            logger.error(f"OCR with confidence error: {str(e)}")
            raise OCRProcessingException(f"OCR with confidence failed: {str(e)}")