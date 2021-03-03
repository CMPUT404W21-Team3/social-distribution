from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.get_profile),
]
