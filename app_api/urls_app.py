# utf-8
from django.urls import path
from app_api import views_app

urlpatterns = [
    path('login/', views_app.LoginView.as_view()),
    path('projects/', views_app.ProjectView.as_view()),
    path('docs/', views_app.DocView.as_view()),
    path('doctemps/', views_app.DocTempView.as_view()),
    path('images/', views_app.ImageView.as_view()),
    path('imggroups/', views_app.ImageGroupView.as_view()),
    path('attachments/', views_app.AttachmentView.as_view()),
]
