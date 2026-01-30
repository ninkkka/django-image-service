from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('upload/', views.upload_page, name='upload_page'),
    path('list/', views.list_page, name='list_page'),
    path('image/<uuid:image_id>/', views.detail_page, name='detail_page'),
    path('api/images/', views.ImageUploadView.as_view(), name='image_upload'),
    path('api/images/list/', views.ImageListView.as_view(), name='image_list'),
    path('api/images/<uuid:image_id>/', views.ImageDetailView.as_view(), name='image_detail'),
]
