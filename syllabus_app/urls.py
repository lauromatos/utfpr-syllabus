from django.urls import path
from syllabus_app import views


urlpatterns = [
    path('', views.index, name='index'),
]