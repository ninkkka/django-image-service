import pytest
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_test')


@pytest.fixture(scope='session')
def django_db_setup():
    """Настройка базы данных для тестов"""
    django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включает доступ к БД для всех тестов с маркером django_db"""
    pass


@pytest.fixture
def test_image_file():
    """Создает тестовое изображение в памяти"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image as PILImage
    from io import BytesIO
    
    file = BytesIO()
    image = PILImage.new('RGB', (100, 100), color='red')
    image.save(file, 'JPEG')
    file.name = 'test_image.jpg'
    file.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=file.read(),
        content_type='image/jpeg'
    )


@pytest.fixture
def test_invalid_file():
    """Создает невалидный файл (не изображение)"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    return SimpleUploadedFile(
        name='test.txt',
        content=b'This is not an image file',
        content_type='text/plain'
    )
