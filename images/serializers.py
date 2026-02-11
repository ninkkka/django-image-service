from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Image"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = ['id', 'title', 'image', 'image_url', 'uploaded_at', 'width', 'height', 'format']
        read_only_fields = ['id', 'uploaded_at', 'width', 'height', 'format']
        extra_kwargs = {
            'image': {'write_only': True}
        }
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            try:
                return request.build_absolute_uri(obj.image.url)
            except:
                return obj.image.url
        return None

class ImageListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка"""
    thumbnail_url = serializers.SerializerMethodField()
    size_kb = serializers.SerializerMethodField()  # Добавили
    
    class Meta:
        model = Image
        fields = ['id', 'title', 'thumbnail_url', 'uploaded_at', 'width', 'height', 'size_kb']  # Добавили поля
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            try:
                return request.build_absolute_uri(obj.image.url)
            except:
                return obj.image.url
        return None
    

    def get_size_kb(self, obj):  # Новый метод
        """Размер в килобайтах"""
        if obj.size:
            return round(obj.size / 1024, 1)
        return 0