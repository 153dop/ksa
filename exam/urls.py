from django.urls import path

from . import views

app_name = 'exam'
urlpatterns = [
    path('exam-in-progress', views.exam),
    path('', views.home_user)
]