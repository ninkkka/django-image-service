import os
from PIL import Image as PILImage
from io import BytesIO
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image
from .serializers import ImageSerializer


class ImageUploadView(APIView):
    """API для загрузки изображений"""
    parser_classes = [MultiPartParser, FormParser]
    

    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем файл и название
            image_file = request.FILES['image']
        
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            file_extension = image_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return Response(
                    {'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем название (используем имя файла если не указано)
            title = request.data.get('title', image_file.name.rsplit('.', 1)[0])
            
            # Создаем объект изображения
            image_instance = Image(
                title=title,
                image=image_file
            )
            
            # Временно сохраняем чтобы получить путь
            image_instance.save()
            
            # Сериализуем и возвращаем ответ
            serializer = ImageSerializer(image_instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImageListView(APIView):
    """API для получения списка всех изображений"""
    

    def get(self, request, *args, **kwargs):
        images = Image.objects.all().order_by('-uploaded_at')
        serializer = ImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


class ImageDetailView(APIView):
    """API для получения, обновления и удаления конкретного изображения"""
    

    def get(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(Image, id=image_id)
        serializer = ImageSerializer(image, context={'request': request})
        return Response(serializer.data)
    

    def delete(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(Image, id=image_id)
        
        # Удаляем файл с диска
        if image.image:
            if os.path.isfile(image.image.path):
                os.remove(image.image.path)
        
        # Удаляем запись из БД
        image.delete()
        
        return Response(
            {'message': 'Image deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


def home_page(request):
    """Главная страница - редирект на страницу загрузки"""
    return render(request, 'images/home.html')


def upload_page(request):
    """Страница загрузки изображения"""
    return render(request, 'images/upload.html')


def list_page(request):
    """Страница просмотра всех изображений"""
    return render(request, 'images/list.html')


def detail_page(request, image_id):
    """Страница просмотра конкретного изображения"""
    return render(request, 'images/detail.html', {'image_id': image_id})
