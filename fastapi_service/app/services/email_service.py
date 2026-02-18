import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from typing import Optional, List
from jinja2 import Template
from ..core.config import settings
from ..core.exceptions import EmailSendingException

logger = logging.getLogger(__name__)

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .ocr-text { background: white; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        .image-info { background: #e8f5e9; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📷 OCR Image Analysis</h1>
        </div>
        <div class="content">
            <p>Здравствуйте!</p>
            <p>Ваше изображение было успешно проанализировано.</p>
            
            <div class="image-info">
                <h3>Информация об изображении:</h3>
                <p><strong>Название:</strong> {{ image_title }}</p>
                <p><strong>ID:</strong> {{ image_id }}</p>
                <p><strong>Дата загрузки:</strong> {{ uploaded_at }}</p>
                <p><strong>Размер:</strong> {{ size }} байт</p>
                <p><strong>Разрешение:</strong> {{ width }}x{{ height }}</p>
                <p><strong>Формат:</strong> {{ format }}</p>
            </div>
            
            <h3>Распознанный текст:</h3>
            <div class="ocr-text">
                {{ ocr_text }}
            </div>
            
            {% if confidence %}
            <p><strong>Уверенность распознавания:</strong> {{ confidence }}%</p>
            {% endif %}
        </div>
        <div class="footer">
            <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
            <p>© {{ year }} Image OCR Service</p>
        </div>
    </div>
</body>
</html>
"""

class EmailService:
    """Сервис для отправки email уведомлений"""
    
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.use_tls = settings.EMAIL_USE_TLS
        self.username = settings.EMAIL_HOST_USER
        self.password = settings.EMAIL_HOST_PASSWORD
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.template = Template(EMAIL_TEMPLATE)
        
        logger.info(f"Email Service initialized with host: {self.host}")
    
    async def send_ocr_result(
        self,
        to_email: str,
        image_data: dict,
        ocr_text: str,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Отправка результатов OCR на email
        """
        try:
            context = {
                'image_title': image_data.get('title', 'Без названия'),
                'image_id': str(image_data.get('id', '')),
                'uploaded_at': image_data.get('uploaded_at', ''),
                'size': image_data.get('size', 0),
                'width': image_data.get('width', 0),
                'height': image_data.get('height', 0),
                'format': image_data.get('format', ''),
                'ocr_text': ocr_text,
                'confidence': confidence,
                'year': '2026'
            }
            
            html_content = self.template.render(**context)
            
            message = MIMEMultipart('alternative')
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = f"Результаты OCR для изображения: {context['image_title']}"
            
            text_part = MIMEText(
                f"Результаты OCR для изображения {context['image_title']}\n\n"
                f"Распознанный текст:\n{ocr_text}",
                'plain'
            )
            message.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            await self._send_email(message)
            
            logger.info(f"✅ OCR results sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            raise EmailSendingException(f"Failed to send email: {str(e)}")
    
    async def send_notification(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Отправка простого уведомления
        """
        try:
            message = MIMEText(body, 'plain')
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject
            
            await self._send_email(message)
            
            logger.info(f"✅ Notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {str(e)}")
            raise EmailSendingException(f"Failed to send notification: {str(e)}")
    
    async def _send_email(self, message: MIMEMultipart):
        """
        Внутренний метод для отправки email через SMTP
        """
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=self.use_tls
            )
            
            await smtp.connect()
            
            if self.username and self.password:
                await smtp.login(self.username, self.password)
            
            await smtp.send_message(message)
            await smtp.quit()
            
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            raise