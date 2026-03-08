from django.urls import path
from . import views


urlpatterns = [
    path('', views.profile, name='profile'),
    path('dashboard/', views.deshboard, name='dashboard'),
    path('about/', views.about, name='about'),
]
