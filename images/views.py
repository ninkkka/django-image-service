from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer, ImageListSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-uploaded_at')
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ImageListSerializer
        return ImageSerializer

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def home_page(self, request):
        return Response(template_name='images/home.html')
    
    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def upload_page(self, request):
        return Response(template_name='images/upload.html')
    
    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def list_page(self, request):
        images = self.get_queryset()
        serializer = ImageListSerializer(images, many=True, context={'request': request})
        return Response({'images': serializer.data}, template_name='images/list.html')
    
    @action(detail=True, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def detail_page(self, request, id=None):
        image = self.get_object()
        serializer = self.get_serializer(image)
        return Response({'image': serializer.data}, template_name='images/detail.html')
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_api(self, request):
        """Отдельный эндпоинт для загрузки через API с токеном"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def home_page(request):
    return render(request, 'images/home.html')

def upload_page(request):
    return render(request, 'images/upload.html')

def list_page(request):
    return render(request, 'images/list.html')

def detail_page(request, image_id):
    return render(request, 'images/detail.html', {'image_id': image_id})
