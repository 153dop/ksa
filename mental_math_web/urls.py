"""mental_math_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views

# Gestion des erreurs avec des pages customisées
handler400 = 'mental_math_web.views.handler400'
handler403 = 'mental_math_web.views.handler403'
handler404 = 'mental_math_web.views.handler404'
handler500 = 'mental_math_web.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', views.home),
    path('exam/', include('exam.urls')),
    path('training/', include('training.urls')),
    path('mental_math_tricks/', views.mental_math_tricks)
]
