from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as Search_views

app_name = 'Search'

urlpatterns = [
    path('search', Search_views.results, name='results'), # see results of search
]
