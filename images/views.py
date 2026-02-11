from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer, ImageListSerializer
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import logging
logger = logging.getLogger(__name__)

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-uploaded_at')
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
    permission_classes = [AllowAny]
    authentication_classes = []
    
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
    
    @action(detail=False, 
            methods=['post'], 
            permission_classes=[AllowAny],
            authentication_classes=[],
            url_path='upload')
    def upload_from_site(self, request):
        """Загрузка с сайта (без токена)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers('Authorization',))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        cache_key = f'image_detail_{instance.id}'
        cached_data = cache.get(cache_key)
        
        logger.info(f"🔑 Cache key: {cache_key}")
        
        if cached_data:
            logger.info(f"✅ CACHE HIT: {cache_key}")
            return Response(cached_data)
        
        logger.info(f"❌ CACHE MISS: {cache_key}")
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        cache.set(cache_key, data, 60 * 10)
        logger.info(f"💾 CACHE SET: {cache_key}")
        
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()
        print("🧹 Cache cleared after create")
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'image_detail_{instance.id}'
        cache.delete(cache_key)
        cache.clear()
        print(f"🗑️ Cache deleted: {cache_key}")
        return super().destroy(request, *args, **kwargs)

def home_page(request):
    return render(request, 'images/home.html')

def upload_page(request):
    return render(request, 'images/upload.html')

def list_page(request):
    return render(request, 'images/list.html')

def detail_page(request, image_id):
    return render(request, 'images/detail.html', {'image_id': image_id})
