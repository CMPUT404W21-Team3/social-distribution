from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models.query import InstanceCheckMeta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponseForbidden
from django.forms import ModelForm
# Create your views here.

from .forms import UserForm, ProfileForm, SignUpForm, PostForm
# Potentially problematic
from .models import Profile, Post
from Search.models import FriendRequest


@login_required(login_url='/login/')
def home(request):
	"""
	Redirect to homepage. Login required
	Parameters
	----------
	Returns
	-------
	Render to the home.html
	"""
	posts = Post.objects.all().order_by('-timestamp')
	return render(request, 'profile/home.html', {'posts':posts})

@login_required(login_url='/login/')
def update_profile(request):
	"""
	Update a user's profile. Login required
	Parameters
	----------
	Handle the POST/GET request
	Returns
	-------
	Either submit the form if POST or view the form.
	"""
	if request.method == 'POST':
		user_form = UserForm(request.POST, instance=request.user)
		profile_form = ProfileForm(request.POST, instance=request.user.profile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, 'Your profile was successfully updated!')
			return redirect('Profile:home')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		user_form = UserForm(instance=request.user)
		profile_form = ProfileForm(instance=request.user.profile)
	return render(request, 'profile/profile.html', {
		'user_form': user_form,
		'profile_form': profile_form
	})

def signup(request):
	"""
	Sign up.
	Parameters
	----------
	Handle the POST request, adding new user.
	Else just render the page
	Returns
	-------
	"""
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.save()
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=user.username, password=raw_password)
			login(request, user)
			messages.success(request, 'Your user was successfully created!')
			return redirect('Profile:profile')
	else:
		form = SignUpForm()
	return render(request, 'profile/signup.html', {'form': form})


def list(request):
	# Fetch friend requests and friends
	friend_requests = FriendRequest.objects.filter(receiver=request.user.username)
	user = Profile.objects.get(user__username=request.user.username)
	friends = user.friends.all()

	return render(request, 'profile/list.html', {'friend_requests': friend_requests, 'friends': friends})

def accept(request):
	# Delete that request
	FriendRequest.objects.filter(receiver=request.user.username).filter(sender=request.POST.get('sender', '')).delete()

	# Add to friends list
	r_user = Profile.objects.get(user__username=request.user.username)
	s_user = Profile.objects.get(user__username=request.POST.get('sender', ''))
	r_user.friends.add(s_user)

	return redirect('/friends')

def decline(request):
	# Delete that request
	FriendRequest.objects.filter(receiver=request.user.username).filter(sender=request.POST.get('sender', '')).delete()
	return redirect('/friends')

def posts(request, author_id):
	author = Profile.objects.get(id=author_id)
	posts = author.posts.all()
	return render(request, 'profile/posts.html', {'posts':posts, 'author':author})

def post(request, author_id, post_id):
	current_user = request.user
	post = get_object_or_404(Post, id=post_id, author__id=author_id)
	return render(request, 'profile/post.html', {'post':post, 'current_user':current_user})

class CreatePostView(generic.CreateView):
	model = Post
	template_name = 'profile/create_post.html'
	fields = ['title', 'source', 'origin', 'content_type', 'description', 'content', 'categories', 'visibility']

	def form_valid(self, form):
		author = self.request.user.profile
		self.success_url = '/author/' + str(author.id) + '/posts'
		form.instance.author = author
		return super().form_valid(form)

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'source', 'origin', 'content_type', 'description', 'content', 'categories', 'visibility']

@login_required(login_url='/login/')
def edit_post(request, post_id):
	post = Post.objects.get(id=post_id)
	if post.author.id != request.user.profile.id:
		return HttpResponseForbidden
	
	if request.method == 'POST':
		post_form = PostForm(request.POST, instance=post)
		if post_form.is_valid():
			post_form.save()
			return redirect('Profile:post', author_id=post.author.id, post_id=post.id)
		else:
			messages.error(request, 'Please correct the error')
	else:
		post_form = PostForm(instance=post)
	return render(request, 'profile/edit_post.html', {'post_form':post_form})

@login_required(login_url='/login/')
def delete_post(request, post_id):
	post = Post.objects.get(id=post_id)
	if post.author.id != request.user.profile.id:
		return HttpResponseForbidden
	else:
		post.delete()
		return redirect('Profile:posts', author_id=request.user.profile.id)

def share_post(request, post_id):
	post = Post.objects.get(id=post_id)
	author_original = post.author
	author_share = request.user.profile
	if request.method == "GET":
		form = PostForm(instance=post, initial={'title': post.title + f'---Shared from {str(author_original)}',\
												'origin': post.origin + f';http://localhost:8000/author/{author_original.id}/posts/{post_id}'})

		return render(request, "profile/create_post.html", {'form':form})
	else:
		form = PostForm(data=request.POST)
		form.instance.author = author_share
		if form.is_valid():
			post_share = form.save(commit=False)
			post_share.save()
			return redirect('Profile:posts', author_share.id)

def view_profile(request, author_id):
	user = Profile.objects.get(user__username=request.user.username)
	author = Profile.objects.get(user_id=author_id)
	friend_status = user.friends.filter(user_id=author_id).exists()
	friend_posts = author.posts.all()

	if request.method == "GET":
		return render(request, 'profile/view_profile.html', {'author': author, 'posts': friend_posts, 'friend_status': friend_status})

def remove_friend(request, author_id):
	user = Profile.objects.get(user__username=request.user.username)
	to_delete = Profile.objects.get(user__id=author_id)
	user.friends.remove(to_delete)

	return redirect('Profile:view_profile', author_id)
