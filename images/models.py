import os
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from PIL import Image as PILImage

def upload_to(instance, filename):
    """Генерируем путь для сохранения файла: media/images/год/месяц/уникальное_имя_файла"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images', str(timezone.now().year), str(timezone.now().month), filename)

class Image(models.Model):
    """Модель для хранения информации об изображениях"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="Название изображения")
    image = models.ImageField(
        upload_to=upload_to,
        verbose_name="Файл изображения",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            )
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    size = models.IntegerField(verbose_name="Размер файла (в байтах)", default=0)
    width = models.IntegerField(verbose_name="Ширина изображения", default=0)
    height = models.IntegerField(verbose_name="Высота изображения", default=0)
    format = models.CharField(max_length=10, verbose_name="Формат файла", default='')

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.format})"

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического вычисления размера и размеров изображения"""
        super().save(*args, **kwargs)
        
        if self.image:
            self.size = self.image.size
            
            self.format = self.image.name.split('.')[-1].lower()
            
            try:
                from PIL import Image as PILImage
                import os
                
                img_path = self.image.path
                
                if os.path.exists(img_path):
                    with PILImage.open(img_path) as img:
                        self.width, self.height = img.size
                else:
                    self.width = 0
                    self.height = 0
                    
            except Exception as e:
                print(f"Ошибка при получении размеров изображения: {e}")
                self.width = 0
                self.height = 0
            
            super().save(update_fields=['size', 'format', 'width', 'height'])
