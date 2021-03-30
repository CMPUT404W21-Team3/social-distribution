from django.urls import include, path
from rest_framework import routers
from . import views

app_name = 'api'

urlpatterns = [
    path('author/<str:author_id>/', views.author, name='author'),
    path('author/<str:author_id>/posts/<str:post_id>', views.post, name='post'),
    path('author/<str:author_id>/posts/', views.posts),
    path('author/<str:author_id>/friends/', views.friends),
    path('author/<str:author_id>/friends/<str:friend_id>', views.friend),
    path('author/<str:author_id>/friendrequests/', views.requests),
    path('author/<str:author_id>/friendrequests/<str:sender_id>', views.request),
    path('author/<str:author_id>/followers', views.followers),
    path('author/<str:author_id>/followers/<str:follower_id>', views.follower),
    path('author/<str:author_id>/posts/<str:post_id>/comments', views.comments),
    path('author/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>', views.comment, name='comment'),
    path('author/<str:author_id>/posts/<str:post_id>/likes', views.post_likes),
    path('author/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.comment_likes),
    path('author/<str:author_id>/liked', views.liked),
    path('author/<str:author_id>/inbox', views.inbox),
    path('authors', views.authors),
    path('posts', views.get_all_posts),
    path('authors/search/<str:query>', views.author_search),
    path('api/author/<str:author_id>/', views.author),
    path('api/author/<str:author_id>/posts/<str:post_id>', views.post),
    path('api/author/<str:author_id>/posts/', views.posts),
    path('api/author/<str:author_id>/friends/', views.friends),
    path('api/author/<str:author_id>/friends/<str:friend_id>', views.friend),
    path('api/author/<str:author_id>/friendrequests/', views.requests),
    path('api/author/<str:author_id>/friendrequests/<str:sender_id>', views.request),
    path('api/author/<str:author_id>/followers', views.followers),
    path('api/author/<str:author_id>/followers/<str:follower_id>', views.follower),
    path('api/author/<str:author_id>/posts/<str:post_id>/comments', views.comments),
    path('api/author/<str:author_id>/posts/<str:post_id>/likes', views.post_likes),
    path('api/author/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.comment_likes),
    path('api/author/<str:author_id>/liked', views.liked),
    path('api/author/<str:author_id>/inbox', views.inbox),
    path('api/authors', views.authors),
    path('api/authors/search?q=<str:query>', views.author_search),
    path('api/authors/search/<str:query>', views.author_search),
    path('api/posts', views.get_all_posts),
    path('api/inbox/<str:author_id>/', views.inbox),

]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
