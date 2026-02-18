import httpx
from uuid import UUID
import logging
from ..core.config import settings
from ..core.exceptions import DjangoAPIException, ImageNotFoundException

logger = logging.getLogger(__name__)

class DjangoService:
    """Сервис для взаимодействия с Django API"""
    
    def __init__(self, base_url: str = settings.DJANGO_API_URL):
        self.base_url = base_url
        self.timeout = settings.DJANGO_API_TIMEOUT
    
    async def get_image(self, image_id: UUID) -> dict:
        """Получение информации об изображении из Django"""
        url = f"{self.base_url}/images/{image_id}/api-data/"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully retrieved image {image_id}")
                    return data
                elif response.status_code == 404:
                    raise ImageNotFoundException(str(image_id))
                else:
                    raise DjangoAPIException(f"Django API error: {response.status_code}")
        except httpx.TimeoutException:
            raise DjangoAPIException("Timeout connecting to Django API")
        except httpx.RequestError as e:
            raise DjangoAPIException(f"Failed to connect to Django API: {str(e)}")
    
    async def get_image_url(self, image_id: UUID) -> str:
        """Получение URL изображения"""
        data = await self.get_image(image_id)
        return data.get('image_url')