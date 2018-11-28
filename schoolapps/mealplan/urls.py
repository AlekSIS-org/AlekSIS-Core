from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="menu_index"),
    path('upload/', views.upload, name="menu_upload")
]
