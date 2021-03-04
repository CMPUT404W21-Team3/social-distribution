from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('author/<str:author_id>/', views.get_author),
    path('author/<str:author_id>/posts/<str:post_id>', views.get_post),
]
