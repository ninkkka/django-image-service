from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class DjangoImageResponse(BaseModel):
    id: UUID
    title: str
    image: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class OCRRequest(BaseModel):
    image_id: UUID = Field(..., description="ID изображения в Django")
    send_email: bool = Field(True, description="Отправлять ли результат на email")
    email: Optional[EmailStr] = Field(None, description="Email для отправки (если не указан, берется из настроек)")

class OCRResponse(BaseModel):
    task_id: str = Field(..., description="ID задачи в Celery")
    status: str = Field("processing", description="Статус обработки")
    message: str = Field("Задача поставлена в очередь", description="Сообщение")

class OCRResultResponse(BaseModel):
    image_id: UUID
    text: str
    confidence: Optional[float] = None
    processed_at: datetime

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    image_id: Optional[UUID] = None
    ocr_text: Optional[str] = None

class EmailResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None