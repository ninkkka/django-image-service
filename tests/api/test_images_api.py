# tests/api/test_images_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from images.models import Image

# Глобальный маркер для ВСЕХ тестов в этом файле
pytestmark = pytest.mark.django_db


class TestImageUploadAPI:
    """Тесты для API загрузки изображений"""
    
    def test_upload_image_success(self, test_image_file):
        """Тест успешной загрузки изображения"""
        client = APIClient()
        response = client.post(
            reverse('image_upload'),
            {'title': 'Test API Image', 'image': test_image_file},
            format='multipart'
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_upload_image_without_title(self, test_image_file):
        """Тест загрузки без указания названия"""
        client = APIClient()
        response = client.post(
            reverse('image_upload'),
            {'image': test_image_file},
            format='multipart'
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_upload_invalid_file_type(self, test_invalid_file):
        """Тест загрузки невалидного типа файла"""
        client = APIClient()
        response = client.post(
            reverse('image_upload'),
            {'title': 'Invalid File', 'image': test_invalid_file},
            format='multipart'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_upload_without_file(self):
        """Тест загрузки без файла"""
        client = APIClient()
        response = client.post(
            reverse('image_upload'),
            {'title': 'No File'},
            format='multipart'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestImageListAPI:
    """Тесты для API получения списка изображений"""
    
    def test_get_empty_list(self):
        """Тест получения пустого списка"""
        client = APIClient()
        response = client.get(reverse('image_list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_get_image_list(self, test_image_file):
        """Тест получения списка с изображениями"""
        client = APIClient()
        Image.objects.create(title="Image 1", image=test_image_file)
        Image.objects.create(title="Image 2", image=test_image_file)
        response = client.get(reverse('image_list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


class TestImageDetailAPI:
    """Тесты для API детальной информации об изображении"""
    
    def test_get_image_detail(self, test_image_file):
        """Тест получения детальной информации"""
        client = APIClient()
        image = Image.objects.create(title="Test Detail", image=test_image_file)
        response = client.get(reverse('image_detail', args=[image.id]))
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_nonexistent_image(self):
        """Тест получения несуществующего изображения"""
        client = APIClient()
        fake_uuid = '12345678-1234-1234-1234-123456789012'
        response = client.get(reverse('image_detail', args=[fake_uuid]))
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_image(self, test_image_file):
        """Тест удаления изображения"""
        client = APIClient()
        image = Image.objects.create(title="To Delete", image=test_image_file)
        response = client.delete(reverse('image_detail', args=[image.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_nonexistent_image(self):
        """Тест удаления несуществующего изображения"""
        client = APIClient()
        fake_uuid = '12345678-1234-1234-1234-123456789012'
        response = client.delete(reverse('image_detail', args=[fake_uuid]))
        assert response.status_code == status.HTTP_404_NOT_FOUND