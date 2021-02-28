from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import generic
# Create your views here.

from .forms import UserForm, ProfileForm, SignUpForm
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
	return render(request, 'profile/home.html')

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
	post = Post.objects.get(id=post_id)
	return render(request, 'profile/post.html', {'post':post})

class CreatePostView(generic.CreateView):
	model = Post
	template_name = 'profile/create_post.html'
	fields = ['title', 'source', 'origin', 'content_type', 'description', 'content', 'categories', 'visibility']	

	def form_valid(self, form):
		author = self.request.user.profile
		self.success_url = '/author/' + str(author.id) + '/posts'
		form.instance.author = author
		return super().form_valid(form)
