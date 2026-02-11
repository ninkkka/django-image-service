from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ImageViewSet 

router = DefaultRouter()
router.register(r'images', views.ImageViewSet, basename='image')

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('upload/', views.upload_page, name='upload_page'),
    path('list/', views.list_page, name='list_page'),
    path('image/<uuid:image_id>/', views.detail_page, name='detail_page'),
    path('api/images/upload/', 
         ImageViewSet.as_view({'post': 'upload_from_site'}), 
         name='image-upload-site'),
    
    path('api/', include(router.urls)),
]