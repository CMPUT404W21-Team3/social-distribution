
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
    url(r'^friends/$', Profile_views.friends_list, name='friends'), # view friends list
    path('author/<str:author_id>/view_posts', Profile_views.view_posts, name='view_posts'), # recent posts by author
    path('author/new_post', Profile_views.CreatePostView.as_view(), name='new_post'), # post creation
    path('author/new_image_post', Profile_views.new_image_post, name='new_image_post'), # image post creation
    path('author/edit_post/<str:post_id>', Profile_views.edit_post, name='edit_post'),
    path('author/delete_post/<str:post_id>', Profile_views.delete_post, name='delete_post'),
    path('author/share_post/<str:author_id>/<str:post_id>/', Profile_views.share_post, name='share_post'),
    path('author/<str:author_id>/view_post/<str:post_id>', Profile_views.view_post, name='view_post'),
    path('view_profile/<str:author_id>', Profile_views.view_profile, name='view_profile'),
    path('view_profile/<str:author_id>/follow', Profile_views.follow, name='follow'), # Follow someone
    path('view_profile/<str:author_id>/unfollow', Profile_views.unfollow, name='unfollow'), # Unfollow someone
    path('view_profile/<str:author_id>/private_post', Profile_views.private_post, name='private_post'),
    path('github_activity/', Profile_views.view_github_activity, name='view_github_activity'),
    path('post_github/', Profile_views.post_github, name='post_github'),
    path('author/<str:author_id>/view_post/<str:post_id>/liked', Profile_views.like_post, name='like'), # like a post
    path('inbox/', Profile_views.inbox, name='inbox'),

]
