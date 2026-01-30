# tests/test_final_coverage.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_test')

import django
django.setup()

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.test import Client
from rest_framework.test import APIClient
from rest_framework import status
from images.models import Image, upload_to
from images.serializers import ImageSerializer
from images.admin import ImageAdmin
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from io import BytesIO
import uuid
from datetime import datetime


class ImageModelTests(TestCase):
    """Тесты модели Image"""
    
    def create_test_image_file(self, color='red', size=100, filename='test.jpg'):
        """Создает тестовое изображение"""
        file = BytesIO()
        image = PILImage.new('RGB', (size, size), color=color)
        image.save(file, 'JPEG' if filename.endswith('.jpg') else 'PNG')
        file.name = filename
        file.seek(0)
        return SimpleUploadedFile(
            name=filename,
            content=file.read(),
            content_type='image/jpeg' if filename.endswith('.jpg') else 'image/png'
        )
    
    def test_create_image(self):
        """Тест создания изображения"""
        image_file = self.create_test_image_file()
        image = Image.objects.create(
            title="Test Image",
            image=image_file
        )
        
        self.assertEqual(image.title, "Test Image")
        self.assertGreater(image.size, 0)
        self.assertIsNotNone(image.id)
    
    def test_image_string_representation(self):
        """Тест строкового представления"""
        image_file = self.create_test_image_file()
        image = Image.objects.create(
            title="My Photo",
            image=image_file
        )
        
        self.assertIn("My Photo", str(image))
    
    def test_image_fields(self):
        """Тест полей модели"""
        fields = [f.name for f in Image._meta.get_fields()]
        expected_fields = ['id', 'title', 'image', 'uploaded_at', 'size', 'width', 'height', 'format']
        
        for field in expected_fields:
            self.assertIn(field, fields)
    
    def test_image_meta(self):
        """Тест Meta класса"""
        self.assertEqual(Image._meta.verbose_name, "Изображение")
        self.assertEqual(Image._meta.verbose_name_plural, "Изображения")
        self.assertEqual(Image._meta.ordering, ['-uploaded_at'])
    
    def test_upload_to_function(self):
        """Тест функции upload_to"""
        filename = "test.jpg"
        result = upload_to(None, filename)
        
        # Проверяем структуру пути
        self.assertIn("images/", result)
        self.assertIn(str(datetime.now().year), result)
        self.assertIn(".jpg", result)


class ViewsTests(TestCase):
    """Тесты HTML views"""
    
    def test_home_page(self):
        """Тест главной страницы"""
        client = Client()
        response = client.get(reverse('home_page'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Image Service')
    
    def test_upload_page(self):
        """Тест страницы загрузки"""
        client = Client()
        response = client.get(reverse('upload_page'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Загрузить')
        self.assertContains(response, 'form')
    
    def test_list_page_empty(self):
        """Тест страницы списка (пустая)"""
        client = Client()
        response = client.get(reverse('list_page'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Все изображения')
    
    def test_list_page_with_images(self):
        """Тест страницы списка с изображениями"""
        # Создаем тестовое изображение
        file = BytesIO()
        image = PILImage.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        
        image_file = SimpleUploadedFile(
            name='test.jpg',
            content=file.read(),
            content_type='image/jpeg'
        )
        
        Image.objects.create(title="Test Image", image=image_file)
        
        client = Client()
        response = client.get(reverse('list_page'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_navigation_links(self):
        """Тест навигационных ссылок"""
        client = Client()
        response = client.get(reverse('home_page'))
        content = response.content.decode()
        
        self.assertIn(reverse('home_page'), content)
        self.assertIn(reverse('upload_page'), content)
        self.assertIn(reverse('list_page'), content)


class APITests(TestCase):
    """Тесты API"""
    
    def create_test_image_file(self):
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
    
    def test_api_list_empty(self):
        """Тест пустого списка API"""
        client = APIClient()
        response = client.get('/api/images/list/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_api_list_with_images(self):
        """Тест списка API с изображениями"""
        client = APIClient()
        image_file = self.create_test_image_file()
        
        # Создаем изображения
        Image.objects.create(title="Image 1", image=image_file)
        Image.objects.create(title="Image 2", image=image_file)
        
        response = client.get('/api/images/list/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_api_get_image_detail(self):
        """Тест получения детальной информации об изображении"""
        client = APIClient()
        image_file = self.create_test_image_file()
        
        image = Image.objects.create(title="Test Detail", image=image_file)
        
        response = client.get(f'/api/images/{image.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Detail")
    
    def test_api_get_nonexistent_image(self):
        """Тест получения несуществующего изображения"""
        client = APIClient()
        fake_uuid = '12345678-1234-1234-1234-123456789012'
        
        response = client.get(f'/api/images/{fake_uuid}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SerializerTests(TestCase):
    """Тесты сериализаторов"""
    
    def test_serializer_fields(self):
        """Тест полей сериализатора"""
        serializer = ImageSerializer()
        
        expected_fields = ['id', 'title', 'image', 'image_url', 'uploaded_at', 
                          'size', 'file_size_mb', 'width', 'height', 'format']
        
        for field in expected_fields:
            self.assertIn(field, serializer.fields)
    
    def test_serializer_get_file_size_mb(self):
        """Тест расчета размера файла в MB"""
        # Создаем изображение
        file = BytesIO()
        image = PILImage.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        
        image_file = SimpleUploadedFile(
            name='test.jpg',
            content=file.read(),
            content_type='image/jpeg'
        )
        
        img = Image.objects.create(title="Test", image=image_file)
        
        serializer = ImageSerializer(img)
        
        self.assertIn('file_size_mb', serializer.data)
        self.assertIsInstance(serializer.data['file_size_mb'], (int, float))
