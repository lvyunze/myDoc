# utf-8
from django.urls import path
from app_api import views

urlpatterns = [
    path('manage_token/', views.manage_token, name='manage_token'),
    path('get_projects/', views.get_projects, name="api_get_projects"),
    path('create_doc/', views.create_doc, name="api_create_doc"),
    path('upload_img/', views.upload_img, name="api_upload_img"),
]
