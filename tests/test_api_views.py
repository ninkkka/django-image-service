import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch, MagicMock
from uuid import uuid4
from images.models import Image

@pytest.mark.django_db
class TestAnalyzeDocAPI:
    
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('analyze-doc')
    
    def test_analyze_doc_success(self, create_test_image):
        image = create_test_image()
        data = {'image_id': str(image.id)}
        
        with patch('images.interfaces.api.views.extract_text_from_image.delay') as mock_task:
            mock_task.return_value.id = 'test_task_id'
            mock_task.return_value.status = 'PENDING'
            
            response = self.client.post(self.url, data, format='json')
            
            assert response.status_code == 200
            assert 'task_id' in response.data
            assert response.data['status'] == 'processing'
            mock_task.assert_called_once_with(str(image.id))
    
    def test_analyze_doc_missing_image_id(self):
        data = {}
        
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == 422
        assert 'detail' in response.data
    
    def test_analyze_doc_invalid_uuid(self):
        data = {'image_id': 'invalid-uuid'}
        
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == 422
        assert 'detail' in response.data
    
    def test_analyze_doc_image_not_found(self):
        data = {'image_id': str(uuid4())}
        
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == 404
        assert 'detail' in response.data

@pytest.mark.django_db
class TestSendMessageToEmailAPI:
    
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('send-to-email')
    
    def test_send_email_success(self, create_test_image):
        image = create_test_image()
        data = {
            'image_id': str(image.id),
            'email': 'test@example.com'
        }
        
        with patch('images.interfaces.api.views.send_analysis_notification.delay') as mock_task:
            mock_task.return_value.id = 'test_task_id'

            response = self.client.post(self.url, data, format='json')

            assert response.status_code == 200
            assert 'task_id' in response.data
            mock_task.assert_called_once_with(str(image.id), 'test@example.com')
    
    def test_send_email_missing_fields(self):
        data = {'image_id': str(uuid4())}
        
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == 422
        assert 'errors' in response.data
    
    def test_send_email_invalid_email(self):
        data = {
            'image_id': str(uuid4()),
            'email': 'invalid-email'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == 422
        assert 'detail' in response.data