# tests/unit/test_views.py
import pytest
from django.urls import reverse
from django.test import Client
from images.models import Image

# Глобальный маркер для ВСЕХ тестов в этом файле
pytestmark = pytest.mark.django_db


class TestHTMLViews:
    """Тесты для HTML views"""
    
    def test_home_page(self):
        """Тест главной страницы"""
        client = Client()
        response = client.get(reverse('home_page'))
        assert response.status_code == 200
        assert 'Image Service' in response.content.decode()
    
    def test_upload_page(self):
        """Тест страницы загрузки"""
        client = Client()
        response = client.get(reverse('upload_page'))
        assert response.status_code == 200
        assert 'Загрузить' in response.content.decode()
    
    def test_list_page_empty(self):
        """Тест страницы списка (пустая)"""
        client = Client()
        response = client.get(reverse('list_page'))
        assert response.status_code == 200
    
    def test_list_page_with_images(self, test_image_file):
        """Тест страницы списка с изображениями"""
        client = Client()
        Image.objects.create(title="Test Image", image=test_image_file)
        response = client.get(reverse('list_page'))
        assert response.status_code == 200
    
    def test_detail_page(self, test_image_file):
        """Тест детальной страницы"""
        client = Client()
        image = Image.objects.create(title="Test Detail", image=test_image_file)
        response = client.get(reverse('detail_page', args=[image.id]))
        assert response.status_code == 200
    
    def test_navigation_links(self):
        """Тест навигационных ссылок"""
        client = Client()
        response = client.get(reverse('home_page'))
        content = response.content.decode()
        assert reverse('home_page') in content
        assert reverse('upload_page') in content