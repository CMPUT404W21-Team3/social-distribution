
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views as Profile_views

app_name = 'Profile'

urlpatterns = [
    url(r'^$', Profile_views.home, name='home'),
    #url('/login/', auth_views.LoginView.as_view(template_name='profile/login.html'), name='login'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='profile/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='Profile:login'), name='logout'),
    url(r'^signup/$', Profile_views.signup, name='signup'),
    url(r'^profile/$', Profile_views.update_profile, name='profile')
]