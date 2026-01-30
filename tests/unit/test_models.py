# tests/unit/test_models.py
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from images.models import Image
from PIL import Image as PILImage
from io import BytesIO

# Глобальный маркер для ВСЕХ тестов в этом файле
pytestmark = pytest.mark.django_db


class TestImageModel:
    """Тесты для модели Image"""
    
    def create_test_image(self):
        """Создает тестовое изображение"""
        file = BytesIO()
        image = PILImage.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        return SimpleUploadedFile(
            name='test.jpg',
            content=file.read(),
            content_type='image/jpeg'
        )
    
    def test_create_image(self):
        """Тест создания изображения"""
        image_file = self.create_test_image()
        image = Image.objects.create(
            title="Test Image",
            image=image_file
        )
        
        image.refresh_from_db()
        assert image.title == "Test Image"
        assert image.size > 0
        print(f"✅ Изображение создано: {image.id}")
    
    def test_image_ordering(self):
        """Тест ordering в Meta классе"""
        image_file1 = self.create_test_image()
        image_file2 = self.create_test_image()
        
        image1 = Image.objects.create(title="Image 1", image=image_file1)
        image2 = Image.objects.create(title="Image 2", image=image_file2)
        
        images = Image.objects.all()
        assert images[0].uploaded_at >= images[1].uploaded_at
    
    def test_image_string_representation(self):
        """Тест строкового представления"""
        image_file = self.create_test_image()
        image = Image.objects.create(title="My Photo", image=image_file)
        
        image.refresh_from_db()
        assert "My Photo" in str(image)
    
    def test_image_fields(self):
        """Тест полей модели"""
        fields = [f.name for f in Image._meta.get_fields()]
        expected_fields = ['id', 'title', 'image', 'uploaded_at', 'size', 'width', 'height', 'format']
        
        for field in expected_fields:
            assert field in fields
    
    def test_image_meta_verbose_names(self):
        """Тест verbose_name в Meta"""
        assert Image._meta.verbose_name == "Изображение"
        assert Image._meta.verbose_name_plural == "Изображения"