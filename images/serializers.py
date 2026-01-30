from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений"""
    image_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 
            'title', 
            'image', 
            'image_url',
            'uploaded_at', 
            'size', 
            'file_size_mb',
            'width', 
            'height', 
            'format'
        ]
        read_only_fields = ['id', 'uploaded_at', 'size', 'width', 'height', 'format']
    

    def get_image_url(self, obj):
        """Возвращает абсолютный URL изображения"""
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    
    def get_file_size_mb(self, obj):
        """Возвращает размер файла в мегабайтах"""
        if obj.size:
            return round(obj.size / (1024 * 1024), 2)
        return 0
