from django.urls import path, re_path
from core.app import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    ]

