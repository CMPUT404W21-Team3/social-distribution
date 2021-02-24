
from django.conf.urls import url, include
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as Profile_views

from rest_framework import routers

app_name = 'Profile'

# router = routers.DefaultRouter()
# router.register(r'profiles', Profile_views.ProfileViewSet)

urlpatterns = [
    url(r'^$', Profile_views.home, name='home'), #homepage
    url(r'^login/$', auth_views.LoginView.as_view(template_name='profile/login.html'), name='login'), #login page, use the default view from django
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='Profile:login'), name='logout'), #logout will direct to the login page
    url(r'^signup/$', Profile_views.signup, name='signup'), #signup
    url(r'^profile/$', Profile_views.update_profile, name='profile'), # view/edit your profile
    url(r'^friends/$', Profile_views.list, name='friends'), # view friends list
    path('accept', Profile_views.accept, name='accept'),
    path('decline', Profile_views.decline, name='decline'),
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
