from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models.query import InstanceCheckMeta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponseForbidden, HttpResponse
from django.forms import ModelForm
from django.views.decorators.cache import cache_page
from django.core.serializers import serialize
from base64 import b64encode, b64decode
import commonmark, requests, ast, json

from django.db.models import Q
from django.http import HttpResponseRedirect
# Create your views here.

from .forms import UserForm, AuthorForm, SignUpForm, PostForm, ImagePostForm, CommentForm

from .models import Author, Post, CommentLike, PostLike
from Search.models import FriendRequest
from api.models import Connection
from api.serializers import AuthorSerializer, PostSerializer

from .helpers import timestamp_beautify

# Create your views here.

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
	# Grab all public posts
	public_posts = Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-timestamp')

	# Grab self posts
	self_posts = Post.objects.filter(author=request.user.author, unlisted=False).order_by('-timestamp')

	# Grab friend's posts
	friends = Author.objects.get(user__username=request.user.username).friends.all()
	friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=friends).order_by('-timestamp')

	# Merge posts, sort them
	local_posts = public_posts | self_posts | friends_posts
	
	posts = []
	posts.append(local_posts)

	remote_posts = []
	
	for connection in Connection.objects.all():
		url = connection.url + 'service/authors'
		response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
		for author in response.json()['items']:
			author_id = author['id']
			new_url = f'{connection.url}service/author/{author_id}/posts/'
			response = requests.get(new_url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
			posts_remote = response.json()['posts']
			if len(posts) > 0:
				for item in posts_remote:
					if item['visibility'] == 'PUBLIC':
						post_id = item['id']
						post = Post(
							id = item['id'],
							author = Author(
								id = item['author']['id'],
								remote_username = item['author']['displayName'],
							),
							timestamp = item['published'],
							title = item['title'],
							content = item['content'],
							contentType = item['contentType'].split(';')[0],						
						)
						remote_posts.append(post)
						# contentType = item['contentType']
						# if contentType == 'text/plain':
						# 	pass
						# elif contentType == 'text/markdown':
						# 	post.content = commonmark.commonmark(post.content)
						# elif contentType == 'image/png;base64':
						# 	post.content = b64decode(post.content.replace('data:image/png;base64,',''))
						# elif contentType == 'application/base64':
						# 	pass
	posts.append(remote_posts)

	return render(request, 'profile/home.html', {'posts': posts})

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
		author_form = AuthorForm(request.POST, instance=request.user.author)
		if user_form.is_valid() and author_form.is_valid():
			user_form.save()
			author_form.save()
			messages.success(request, 'Your profile was successfully updated!')
			return redirect('Profile:home')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		user_form = UserForm(instance=request.user)
		author_form = AuthorForm(instance=request.user.author)
	return render(request, 'profile/profile.html', {
		'user_form': user_form,
		'author_form': author_form
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
			user.refresh_from_db()
			user.is_active = False  # load the profile instance created by the signal
			user.save()
			messages.success(request, 'Your user was successfully created!')
			return redirect('Profile:login')
	else:
		form = SignUpForm()
	return render(request, 'profile/signup.html', {'form': form})


def list(request):
	user = Author.objects.get(user__username=request.user.username)
	friend_requests = FriendRequest.objects.filter(receiver=user)
	friends = user.friends.all()
	following = user.following.all()

	# friends = list(friends)

	# Remote friends + followers
	for connection in Connection.objects.all():
		url = connection.url + '/service/author/' + str(user.id) + '/friends'
		response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))

		if response.status_code == 200:
			for friend in response.json()['items']:
				# Filter by response
				friends.append(friend)

			for following in followers:
				url = connection.url + '/service/author/' + str(following.id)
				response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
				if response.status_code == 200:
					follwing.append(response.json()['items'][0])

	return render(request, 'profile/list.html', {'friend_requests': friend_requests, 'friends': friends, 'following': following})

def accept(request):
	receiver = Author.objects.get(user__username=request.user.username)
	sender = Author.objects.get(user__username=request.POST.get('sender', ''))
	# Delete that request
	FriendRequest.objects.filter(receiver=receiver).filter(sender=sender).delete()

	# Add to friends list
	receiver.friends.add(sender)
	receiver.followers.add(sender)

	return redirect('Profile:friends')

def decline(request):
	receiver = Author.objects.get(user__username=request.user.username)
	sender = Author.objects.get(user__username=request.POST.get('sender', ''))
	# Delete that request
	FriendRequest.objects.filter(receiver=receiver).filter(sender=sender).delete()
	return redirect('Profile:friends')

def view_posts(request, author_id):
	author = Author.objects.get(id=author_id)
	posts = author.posts.all()
	if author.id != request.user.author.id: # Only show unlisted posts if viewed by the owner
		posts.filter(unlisted=False)
	return render(request, 'profile/posts.html', {'posts':posts, 'author':author})

def view_post(request, author_id, post_id):
	
	current_user = request.user
	try:
		post = Post.objects.get(id=post_id, author__id=author_id)

		liked = False

		#--- Comments Block ---#
		# https://djangocentral.com/creating-comments-system-with-django/
		if current_user.author.id == post.author.id or post.visibility=='PUBLIC':
			comments = post.comments
		else:
			comments = post.comments.filter(author__id=current_user.author.id)
		new_comment = None
		if request.method == 'POST':
			comment_form = CommentForm(data=request.POST)
			if comment_form.is_valid():
				new_comment = comment_form.save(commit=False)
				new_comment.post = post
				new_comment.author = request.user.author
				new_comment.save()
				# new_comment = CommentForm()
				# ref: https://stackoverflow.com/questions/5773408/how-to-clear-form-fields-after-a-submit-in-django
				# Bugged
				# return HttpResponseRedirect('')
				comment_form = CommentForm()
		else:
			comment_form = CommentForm()
		#--- end of Comments Block ---#

		try:
			obj = PostLike.objects.get(post_id=post, author__id=request.user.author.id)
		except:
			liked = False
		else:
			liked = True

		if post.contentType == Post.ContentType.MARKDOWN:
					post.content = commonmark.commonmark(post.content)
		if post.contentType == Post.ContentType.PNG or post.contentType == Post.ContentType.JPEG:
			return HttpResponse(b64decode(post.content), contentType=post.contentType)
		else:
			return render(request, 'profile/post.html', {'post':post, 'current_user':current_user, 'liked':liked, 'comments':comments, 'comment_form':comment_form})
	except:
		# Remote post
		for connection in Connection.objects.all():
			url = connection.url + 'service/author/' + author_id + '/posts/' + post_id
			response = requests.get(url)
			if response.status_code == 200:
				post = response.json()
				liked = False # TODO need to get like status
				comment_form = CommentForm() # TODO Need to make this work for remote
				comments = post['comments']
				if post['contentType'] == Post.ContentType.MARKDOWN:
					post['content'] = commonmark.commonmark(post['content'])
				print(post['content'])
				if post['contentType'] == Post.ContentType.PNG or post['contentType'] == Post.ContentType.JPEG:
					return HttpResponse(b64decode(post.content), contentType=post.contentType)
				else:
					return render(request, 'profile/post.html', {'post':post, 'current_user':current_user, 'liked':liked, 'comments':comments, 'comment_form':comment_form})

	

class CreatePostView(generic.CreateView):
	model = Post
	template_name = 'profile/create_post.html'
	fields = ['title', 'source', 'origin', 'contentType', 'description', 'content', 'categories', 'visibility', 'unlisted']

	def form_valid(self, form):
		author = self.request.user.author
		self.success_url = '/author/' + str(author.id) + '/view_posts'
		form.instance.author = author
		return super().form_valid(form)

@login_required(login_url='/login/')
def new_image_post(request):
	if request.method == 'POST':
		form = ImagePostForm(request.POST, request.FILES)
		if form.is_valid():
			image_post = form.save(commit=False)
			image_post.content = b64encode(request.FILES['image'].read()).decode('ascii') # https://stackoverflow.com/a/45151058
			image_post.contentType = request.FILES['image'].contentType
			image_post.author = request.user.author
			image_post.unlisted = True
			image_post.save()
			form.save_m2m() # https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#the-save-method
			return redirect('Profile:view_posts', author_id=request.user.author.id)

	else:
		form = ImagePostForm()
		return render(request, 'profile/create_image_post.html', {'form':form})


@login_required(login_url='/login/')
def edit_post(request, post_id):
	post = Post.objects.get(id=post_id)
	if post.author.id != request.user.author.id:
		return HttpResponseForbidden()

	if request.method == 'POST':
		post_form = PostForm(request.POST, instance=post)
		if post_form.is_valid():
			post_form.save()
			return redirect('Profile:view_post', author_id=post.author.id, post_id=post.id)
		else:
			messages.error(request, 'Please correct the error')
	else:
		post_form = PostForm(instance=post)
	return render(request, 'profile/edit_post.html', {'post_form':post_form})

@login_required(login_url='/login/')
def delete_post(request, post_id):
	post = Post.objects.get(id=post_id)
	if post.author.id != request.user.author.id:
		return HttpResponseForbidden()
	else:
		post.delete()
		return redirect('Profile:view_posts', author_id=request.user.author.id)

def share_post(request, post_id, author_id):

	post = None
	try:
		post = Post.objects.get(id=post_id)
		author_original = post.author
		author_share = request.user.author
		if request.method == "GET":
			form = PostForm(instance=post, initial={'title': post.title + f'---Shared from {str(author_original.displayName)}',\
													'origin': post.origin + f'http://localhost:8000/author/{author_original.id}/view_post/{post_id}', \
													'visibility': post.visibility})

			return render(request, "profile/share_post.html", {'form':form})
		else:
			form = PostForm(data=request.POST)
			form.instance.author = author_share
			if form.is_valid():
				post_share = form.save(commit=False)
				post_share.save()
				return redirect('Profile:view_posts', author_share.id)
			else:
				print(form.errors)
		
	except:
		# Sharing remote post
		for connection in Connection.objects.all():
			url = connection.url + 'service/author/' + author_id + '/posts/' + post_id
			response = requests.get(url)
			if response.status_code == 200:
				post_j = response.json()
				# author.save()
				post_j['title'] += "-- Shared from " + post_j['author']['displayName']
				post_j['author'] = request.user.author
				post_j.pop('categories', None)
				post_j.pop('comments', None)
				post_j.pop('count', None)
				post_j.pop('published', None)
				post_j['unlisted'] = 'False'
				print(post_j)
				post = Post.objects.create(**post_j)
				post.save()
				return redirect('Profile:view_posts', request.user.author.id)

		

def view_github_activity(request):
	#get the current user's github username if available
	#need a helper function to get timestamp in a better format
	try:
		github_username = str(request.user.author.github)
		github_url = f'https://api.github.com/users/{github_username}/events/public'
		response = requests.get(github_url)
		jsonResponse = response.json()
		activities = []

		for event in jsonResponse:
			activity = {}
			activity["timestamp"] = timestamp_beautify(event["created_at"])
			repo = event["repo"]["name"]
			payload = event["payload"]

			try:
				if event["type"] == "PushEvent":
					activity["EventType"] = "PushEvent"
					head_sha = payload["head"]
					url = f"http://github.com/{repo}/commit/{head_sha}"
					activity["url"] = url
					size = payload["size"]
					activity["message"] = payload["commits"][size-1]["message"]
					activities.append(activity)
			except:
				pass

			try:
				if event["type"] == "PullRequestEvent":
					activity["EventType"] = "PullRequestEvent"
					pull_request = payload["pull_request"]
					activity["url"] = pull_request["html_url"]
					activity["message"] = f'{pull_request["title"]} #{pull_request["number"]}'
					activities.append(activity)
			except:
				pass

			try:
				if event["type"] == "CreateEvent":
					activity["EventType"] = "CreateEvent"
					activity["url"] = "No URL source"
					activity["message"] = f"Created a {payload['ref_type']} called {payload['ref']}"
					activities.append(activity)
			except:
				pass

			try:
				if event["type"] == "DeleteEvent":
					activity["EventType"] = "DeleteEvent"
					activity["url"] = "No URL source"
					activity["message"] = f"Deleted a {payload['ref_type']} called {payload['ref']}"
					activities.append(activity)
			except:
				pass

			try:
				if event["type"] == "IssuesEvent":
					activity["EventType"] = "IssuesEvent"
					activity["url"] = payload["issue"]["html_url"]
					activity["message"] = f"Issue: {payload['issue']['title']}"
					activities.append(activity)
			except:
				pass

		return render(request, 'profile/github_activity.html', {'github_activity': activities})
	except:
		return render(request, 'profile/github_activity.html')

def post_github(request):
	author = request.user.author
	if request.method == "GET":
		content = ast.literal_eval(request.GET.get("activity"))
		form = PostForm(initial={
			'title': 'Sharing an activity from Github!',
			'origin': '',
			'source': content['url'],
			'content': f"{content['message']}\nTimestamp: {content['timestamp']}\nSource:{content['url']}"
			})
		return render(request, "profile/create_post.html", {'form':form})
	else:
		form = PostForm(data=request.POST)
		form.instance.author = author
		if form.is_valid():
			post = form.save(commit=False)
			post.save()
			return redirect('Profile:view_posts', author.id)


def view_profile(request, author_id):
	user = Author.objects.get(user__username=request.user.username)
	local = True

	# Try to grab from local server
	try:
		found_author = Author.objects.get(id=author_id)
		posts = found_author.posts.all()

	except:
		# Remote author!
		local = False
		for connection in Connection.objects.all():
			url = connection.url + 'service/authors'
			response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
			for author in response.json()['items']:
				# Found a match!
				if author_id == author['id']:
					# Grab posts
					url = connection.url + 'service/author/' + author_id + '/posts'
					response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
					posts = response.json()['posts']

					# Set correct author
					found_author = author


	following_status = user.following.filter(id=author_id).exists()
	follower_status = user.followers.filter(id=author_id).exists()
	if following_status or follower_status:
		follow_status = True
	else:
		follow_status = False
	friend_status = user.friends.filter(id=author_id).exists()

	if request.method == "GET":
		return render(request, 'profile/view_profile.html', {'author': found_author, 'posts': posts, 'friend_status': friend_status, 'follow_status': follow_status, 'local': local})

def friend_request(request, author_id):
	# Create request object

	sender = request.user.author

	local = True
	try:
		receiver = Author.objects.get(id=author_id)
	except:
		local = False
		for connection in Connection.objects.all():
			url = connection.url + 'service/authors'
			response = requests.get(url, headers={"mode":"no-cors"}, auth=('CitrusNetwork', 'oranges'))
			for author in response.json()['items']:
				# Found a match!
				if author_id == author['id']:
					receiver = author
					
					post_data = {}
					post_data['type'] = 'follow'
					post_data['summary'] = sender.displayName + ' wants to follow ' + receiver['displayName']
					post_data['actor'] = AuthorSerializer(sender).data
					post_data['object'] = receiver

					# print(post_data)
					# Send request to remote
					url = connection.url + 'service/author/' + receiver['id'] + '/inbox/'
					# print(url)
					post_response = requests.post(url, json.dumps(post_data), auth=('CitrusNetwork', 'oranges'))
					print(post_response.content)
	
	if local:
		# check if request has already been made

		# print("Receiver = ", receiver.displayName)

		friend_request = FriendRequest(sender=sender, receiver=receiver)

		# Add to database
		friend_request.save()
		# Add the receiver to the sender's following list
		sender.following.add(receiver)
		receiver.followers.add(sender)

	return redirect('Profile:view_profile', author_id)

def remove_friend(request, author_id):
	user = Author.objects.get(user__username=request.user.username)
	to_delete = Author.objects.get(id=author_id)
	user.friends.remove(to_delete)

	return redirect('Profile:view_profile', author_id)



def like_post(request, author_id, post_id):
	current_user = request.user
	post = get_object_or_404(Post, id=post_id, author__id=author_id)
	liked = False

	try:
		obj = PostLike.objects.get(post_id=post, author__id=request.user.author.id)
	except:
		author = Author.objects.get(id=request.user.author.id)
		like_instance = PostLike(post_id=post, author=author)
		like_instance.save()
		post.likes_count = post.likes_count + 1
		post.save()
		liked = True
	else:
		post.likes_count -= 1
		post.save()
		obj.delete()

	if post.contentType == Post.ContentType.PLAIN:
		content = post.content
	if post.contentType == Post.ContentType.MARKDOWN:
		content = commonmark.commonmark(post.content)
	else:
		content = 'Content type not supported yet'
	if current_user.author.id == post.author.id or post.visibility == 'PUBLIC':
		comments = post.comments
	else:
		comments = post.comments.filter(author__id=current_user.author.id)
	comment_form = CommentForm()
	return render(request, 'profile/post.html', {'post':post, 'content':content, 'current_user':current_user, 'liked': liked, 'comments':comments, 'comment_form':comment_form})

def private_post(request, author_id):
	author = request.user.author
	to_author = Author.objects.get(id=author_id)
	if request.method == "GET":
		form = PostForm(initial={'title': f'Private DM from @{author.displayName} --',\
								 'origin': f'http://localhost:8000/view_profile/{author.id}',\
								 'visibility': 'PRIVATE',\
								 'to_author_id': to_author})

		return render(request, "profile/private_post.html", {'form':form})
	elif request.method == "POST":
		form = PostForm(data=request.POST)
		form.instance.author = author
		form.instance.to_author = to_author
		if form.is_valid():
			post_share = form.save(commit=False)
			post_share.save()
			return redirect('Profile:view_posts', author.id)
		else:
			print(form.errors)

def inbox(request):
	author = Author.objects.get(id=request.user.author.id)
	# Private means direct DM or from someone is not your friend (yet)
	private_posts = Post.objects.filter(to_author=request.user.author.id)
	friends = author.friends.all()
	# Friends posts contain all the post from the people you follow
	friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=friends)
	posts = private_posts | friends_posts
	if request.method == "GET":
		inbox_option = request.GET.get("inbox_option")
		if inbox_option == "All":
			posts = posts.order_by('-timestamp')
		elif inbox_option == "Cleared":
			posts = author.posts_cleared.all().order_by('-timestamp')
		else:
			posts = posts.difference(author.posts_cleared.all()).order_by('-timestamp')
		return render(request, 'profile/posts.html', {'posts':posts, 'author':author, 'inbox':True})
	elif request.method == "POST":
		if "clear_signal" in request.POST:
			author.posts_cleared.add(*posts)
		posts = posts.difference(author.posts_cleared.all()).order_by('-timestamp')
		return render(request, 'profile/posts.html', {'posts':posts, 'author':author, 'inbox':True})
