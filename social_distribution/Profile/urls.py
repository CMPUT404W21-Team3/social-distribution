
from django.conf.urls import url, include
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as Profile_views

app_name = 'Profile'

urlpatterns = [
    url(r'^$', Profile_views.home, name='home'), #homepage
    url(r'^login/$', auth_views.LoginView.as_view(template_name='profile/login.html'), name='login'), #login page, use the default view from django
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='Profile:login'), name='logout'), #logout will direct to the login page
    url(r'^signup/$', Profile_views.signup, name='signup'), #signup
    url(r'^profile/$', Profile_views.update_profile, name='profile'), # view/edit your profile
    url(r'^friends/$', Profile_views.list, name='friends'), # view friends list
    path('accept', Profile_views.accept, name='accept'),
    path('decline', Profile_views.decline, name='decline'),
    path('author/<int:author_id>/posts', Profile_views.posts, name='posts'), # recent posts by author
    path('author/new_post', Profile_views.CreatePostView.as_view(), name='new_post'), # post creation
    path('author/edit_post/<int:post_id>', Profile_views.edit_post, name='edit_post'),
    path('author/delete_post/<int:post_id>', Profile_views.delete_post, name='delete_post'),    
    path('author/share_post/<int:post_id>/', Profile_views.share_post, name='share_post'),
    path('author/<int:author_id>/posts/<int:post_id>', Profile_views.post, name='post'),
    path('view_profile/<int:author_id>', Profile_views.view_profile, name='view_profile'),
    path('view_profile/<int:author_id>/remove_friend', Profile_views.remove_friend, name='remove_friend'), # remove a friend
]
