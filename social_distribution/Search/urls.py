from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as Search_views

app_name = 'Search'

urlpatterns = [
    path('search', Search_views.results, name='results'), # see results of search
    path('sendrequest', Search_views.friend_request, name='friend_request'), # send a friend request
]
