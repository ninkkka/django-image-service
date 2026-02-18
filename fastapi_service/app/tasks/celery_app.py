from celery import Celery
from celery.signals import task_failure, task_success, task_prerun
import logging
import asyncio
from typing import Optional
from uuid import UUID

from ..core.config import settings
from ..services.ocr_service import OCRService
from ..services.email_service import EmailService
from ..services.django_service import DjangoService

logger = logging.getLogger(__name__)

celery_app = Celery(
    'ocr_tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.celery_app']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
)

@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    logger.info(f"🚀 Task {task.name}[{task_id}] started")

@task_success.connect
def task_success_handler(sender, result, **kwargs):
    logger.info(f"✅ Task {sender.name}[{sender.request.id}] succeeded")

@task_failure.connect
def task_failure_handler(sender, task_id, exception, *args, **kwargs):
    logger.error(f"❌ Task {sender.name}[{task_id}] failed: {str(exception)}")

@celery_app.task(bind=True, name='process_ocr_task')
def process_ocr_task(self, image_id: str, send_email: bool = True, email: Optional[str] = None):
    """
    Асинхронная задача для обработки OCR
    """
    logger.info(f"📸 Starting OCR task for image {image_id}")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            _process_ocr_async(image_id, send_email, email, self.request.id)
        )
        
        loop.close()
        
        logger.info(f"✅ OCR task completed for image {image_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ OCR task failed for image {image_id}: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)
        raise

async def _process_ocr_async(
    image_id: str, 
    send_email: bool, 
    email: Optional[str],
    task_id: str
) -> dict:
    """
    Асинхронная логика OCR обработки
    """
    django_service = DjangoService()
    ocr_service = OCRService()
    email_service = EmailService()
    
    try:
        logger.info(f"Step 1: Getting image data for {image_id}")
        image_data = await django_service.get_image(UUID(image_id))
        
        if not image_data.image_url:
            raise ValueError("Image URL not found")
        
        logger.info(f"Step 2: Extracting text from {image_data.image_url}")
        ocr_result = await ocr_service.extract_text_with_confidence(image_data.image_url)
        
        if send_email:
            logger.info(f"Step 3: Sending email")
            to_email = email or settings.DEFAULT_FROM_EMAIL
            
            if to_email:
                await email_service.send_ocr_result(
                    to_email=to_email,
                    image_data={
                        'id': image_id,
                        'title': image_data.title,
                        'uploaded_at': str(image_data.uploaded_at),
                        'size': getattr(image_data, 'size', 0),
                        'width': getattr(image_data, 'width', 0),
                        'height': getattr(image_data, 'height', 0),
                        'format': getattr(image_data, 'format', '')
                    },
                    ocr_text=ocr_result['text'],
                    confidence=ocr_result['confidence']
                )
        
        return {
            'task_id': task_id,
            'image_id': image_id,
            'status': 'completed',
            'text': ocr_result['text'],
            'confidence': ocr_result['confidence'],
            'email_sent': send_email
        }
        
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        raise

@celery_app.task(name='health_check')
def health_check():
    """Задача для проверки здоровья Celery"""
    return {'status': 'healthy', 'timestamp': '2026-02-16'}