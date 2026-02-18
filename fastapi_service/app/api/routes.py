from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from uuid import UUID
import logging

from ..models.schemas import OCRRequest, OCRResponse, EmailRequest, EmailResponse, OCRResultResponse
from ..api.dependencies import get_services, Services
from ..tasks.celery_app import process_ocr_task
from ..core.exceptions import ImageNotFoundException, OCRProcessingException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["OCR"])

@router.post("/analyze_doc", response_model=OCRResponse)
async def analyze_doc(
    request: OCRRequest,
    services: Services = Depends(get_services)
):
    """
    Эндпоинт для запуска OCR анализа изображения
    
    - **image_id**: UUID изображения из Django
    - **send_email**: отправлять ли результат на email
    - **email**: email для отправки (если не указан, берется из настроек)
    """
    logger.info(f"📝 Received analyze_doc request for image {request.image_id}")
    
    try:
        image_data = await services.django_service.get_image(request.image_id)
        
        if not image_data:
            raise ImageNotFoundException(str(request.image_id))
        
        task = process_ocr_task.delay(
            image_id=str(request.image_id),
            send_email=request.send_email,
            email=str(request.email) if request.email else None
        )
        
        logger.info(f"✅ OCR task created with ID: {task.id}")
        
        return OCRResponse(
            task_id=task.id,
            status="processing",
            message="Задача поставлена в очередь обработки"
        )
        
    except ImageNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating OCR task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Получение статуса задачи по ID
    """
    from celery.result import AsyncResult
    from ..tasks.celery_app import celery_app
    
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Задача ожидает выполнения'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Ошибка выполнения',
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'result': task.result if task.ready() else None
        }
    
    return response

@router.post("/send_message_to_email", response_model=EmailResponse)
async def send_message_to_email(
    request: EmailRequest,
    services: Services = Depends(get_services)
):
    """
    Эндпоинт для отправки email уведомления
    
    - **to_email**: email получателя
    - **subject**: тема письма
    - **body**: текст письма
    - **image_id**: ID изображения (опционально)
    - **ocr_text**: распознанный текст (опционально)
    """
    logger.info(f"📧 Received send_message_to_email request to {request.to_email}")
    
    try:
        image_data = None
        if request.image_id:
            try:
                image_data = await services.django_service.get_image(request.image_id)
            except Exception as e:
                logger.warning(f"Could not fetch image data: {str(e)}")
        
        body = request.body
        if request.ocr_text and image_data:
            body += f"\n\nOCR Results for {image_data.title}:\n{request.ocr_text}"
        
        success = await services.email_service.send_notification(
            to_email=request.to_email,
            subject=request.subject,
            body=body
        )
        
        return EmailResponse(
            success=success,
            message="Email sent successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        return EmailResponse(
            success=False,
            message=f"Failed to send email: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        'status': 'healthy',
        'service': 'FastAPI OCR Service',
        'version': '1.0.0'
    }

@router.get("/result/{image_id}", response_model=Optional[OCRResultResponse])
async def get_ocr_result(
    image_id: UUID,
    services: Services = Depends(get_services)
):
    """
    Получение последнего результата OCR для изображения
    """
    return None