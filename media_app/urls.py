# media_app/urls.py
from django.urls import path
from . import views

app_name = "media_app"

urlpatterns = [
    path("upload/", views.upload_media, name="upload_media"),  # optional if you want a separate upload
    path("delete/<int:pk>/", views.delete_media, name="delete_media"),
]
