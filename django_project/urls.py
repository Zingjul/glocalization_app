"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),  # ✅ Your custom views
    path('user/', include("person.urls")),
    path("api/", include("custom_search.urls")),  # ✅ This must be here!
    
    path('', include("posts.urls")),
    path('comments/', include("comment.urls")),
    path('search/', include("search.urls")),
    path('custom_search/', include('custom_search.urls')),
    path('postfinder/', include("postfinder.urls")),
    path('seekers/', include('seekers.urls', namespace="seekers")),
    path('seekersfinder/', include('seekersfinder.urls', namespace="seekersfinder")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)