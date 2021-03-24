from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('author/<str:author_id>/', views.get_author),
    path('author/<str:author_id>/posts/<str:post_id>', views.get_post),
    path('author/<str:author_id>/posts/', views.get_posts),
    path('author/<str:author_id>/followers', views.get_followers),
    path('author/<str:author_id>/followers/<str:follower_id>', views.get_follower),
    path('author/<str:author_id>/posts/<str:post_id>/comments', views.get_comments),
    path('api/author/<str:author_id>/', views.get_author),
    path('api/author/<str:author_id>/posts/<str:post_id>', views.get_post),
    path('api/author/<str:author_id>/posts/', views.get_posts),
    path('api/author/<str:author_id>/followers', views.get_followers),
    path('api/author/<str:author_id>/followers/<str:follower_id>', views.get_follower),
    path('api/author/<str:author_id>/posts/<str:post_id>/comments', views.get_comments),
    path('api/inbox/<str:author_id>/', views.inbox),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
