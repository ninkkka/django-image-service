from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'format', 'size', 'uploaded_at', 'width', 'height')
    list_filter = ('format', 'uploaded_at')
    search_fields = ('title',)
    readonly_fields = ('size', 'width', 'height', 'format', 'uploaded_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'image')
        }),
        ('Информация о файле', {
            'fields': ('format', 'size', 'width', 'height', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
