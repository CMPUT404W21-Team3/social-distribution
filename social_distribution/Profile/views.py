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

from .models import Author, Post, CommentLike, PostLike, Inbox
from Search.models import FriendRequest
from api.models import Connection
from api.serializers import AuthorSerializer, PostSerializer

from .helpers import timestamp_beautify

DEFAULT_HEADERS = {'Referer': 'https://team3-socialdistribution.herokuapp.com/', 'Mode': 'no-cors'}

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

	# Grab posts from those who are following
	following = Author.objects.get(user__username=request.user.username).following.all()
	following_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=following).order_by('-timestamp')

	# Merge posts, sort them
	local_posts = public_posts | self_posts | following_posts

	posts = []
	posts.append(local_posts)

	remote_posts = []

	for connection in Connection.objects.all():
		if connection.name == 'localhost':
			pass
		else:
			url = connection.url + 'service/authors/'
			response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
			if response.status_code == 200:
				for author in response.json()['items']:
					author_id = author['id']
					new_url = f'{connection.url}service/author/{author_id}/posts/'
					response = requests.get(new_url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
					if response.status_code == 200:
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

	following = user.following.all()
	followers = user.followers.all()

	# Grab friends
	friends = following & followers

	if user.remote_following_uuid:
		following_remote = user.remote_following_uuid.strip().split(" ")
	else:
		following_remote = None

	if user.remote_followers_uuid:
		followers_remote = user.remote_followers_uuid.strip().split(" ")
	else:
		followers_remote = None

	friends_remote = []
	if following_remote and followers_remote:
		for f in following_remote:
			if f in followers_remote:
				friends_remote.append(f)

	# Remote friends + following
	# Un-comment this for interaction with Citrus
	# Un-comment line 32+52 in list.html as well
	# For local testing sake, i'll just use the uuid string.

	# replacing every uuid as an author object.
	for connection in Connection.objects.all():
		if friends_remote:
			try:
				for i in range(len(friends_remote)):
					url = f'{connection.url}/service/author/' + friends_remote[i] + '/'
					response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))

					if response.status_code == 200:
						friends_remote[i] = response.json()
					else:
						pass #this guy doesn't exist!
			except:
				pass

		if following_remote:
			try:
				for i in range(len(following_remote)):
					url = f'{connection.url}/service/author/' + following_remote[i] + '/'
					response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))

					if response.status_code == 200:
						following_remote[i] = response.json()
					else:
						pass #this guy doesn't exist!
			except:
				pass

		if followers_remote:
			try:
				for i in range(len(followers_remote)):
					url = f'{connection.url}/service/author/' + followers_remote[i] + '/'
					response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))

					if response.status_code == 200:
						followers_remote[i] = response.json()
					else:
						pass #this guy doesn't exist!
			except:
				pass

	return render(request, 'profile/list.html', {'friends': friends, 'friends_remote': friends_remote,
				'following': following, 'following_remote': following_remote, 'followers': followers, 'followers_remote': followers_remote})

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
			post.content = post.content[len(post.contentType) + 6:] # remove "data:image/jpeg;base64," or "data:image/png;base64," from content to leave just b64 encoding
			return HttpResponse(b64decode(post.content), content_type=post.contentType)
		else:
			return render(request, 'profile/post.html', {'post':post, 'current_user':current_user, 'liked':liked, 'comments':comments, 'comment_form':comment_form})
	except:
		# Remote post
		for connection in Connection.objects.all():
			url = connection.url + 'service/author/' + author_id + '/posts/' + post_id + '/'
			response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
			if response.status_code == 200:
				post = response.json()
				liked = False # TODO need to get like status
				comment_form = CommentForm() # TODO Need to make this work for remote
				comments = post['comments']

				if post['contentType'] == Post.ContentType.PNG or post['contentType'] == Post.ContentType.JPEG:
					post['content'] = post['content'].split(',')[-1] # remove "data:image/jpeg;base64," or "data:image/png;base64," from content to leave just b64 encoding
					return HttpResponse(b64decode(post['content']), content_type=post['contentType'])

				if post['contentType'] == Post.ContentType.MARKDOWN:
					post['content'] = commonmark.commonmark(post['content'])

				return render(request, 'profile/post.html', {'post':post, 'current_user':current_user, 'liked':liked, 'comments':comments, 'comment_form':comment_form})
			else:
				return redirect('Profile:home')



class CreatePostView(generic.CreateView):
	model = Post
	template_name = 'profile/create_post.html'
	fields = ['title', 'source', 'origin', 'contentType', 'description', 'content', 'categories', 'visibility', 'unlisted']

	def form_valid(self, form):
		author = self.request.user.author
		self.success_url = '/author/' + str(author.id) + '/view_posts'
		form.instance.author = author

		# https://stackoverflow.com/questions/32998300/django-createview-how-to-perform-action-upon-save
		response = super().form_valid(form)

		for follower in author.followers.all():
			follower.inbox.post_items.add(form.instance)

		return response

@login_required(login_url='/login/')
def new_image_post(request):
	if request.method == 'POST':
		form = ImagePostForm(request.POST, request.FILES)
		if form.is_valid():
			image_post = form.save(commit=False)
			image_post.content = b64encode(request.FILES['image'].read()).decode('ascii') # https://stackoverflow.com/a/45151058
			image_post.contentType = request.FILES['image'].content_type + ';base64'
			image_post.content = 'data:' + image_post.contentType + ',' + image_post.content
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
			url = connection.url + 'service/author/' + author_id + '/posts/' + post_id + '/'
			response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
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
		following_status = user.following.filter(id=author_id).exists()
		follower_status = user.followers.filter(id=author_id).exists()
	except:
		# Remote author!
		local = False
		for connection in Connection.objects.all():
			if connection.name == "localhost":
				found_author = Author(
					id=author_id,
					remote_username='Local Tester'
				)
				posts = None
				try:
					following_status = True if author_id in user.remote_following_uuid else False
				except:
					following_status = False
				
				try:
					follower_status = True if author_id in user.remote_followers_uuid else False
				except:
					follower_status = False
			else:
				url = connection.url + 'service/authors/'
				response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
				if response.status_code == 200:
					for author in response.json()['items']:
						# Found a match!
						if author_id == author['id']:
							# Grab posts
							url = connection.url + 'service/author/' + author_id + '/posts/'
							response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
							if response.status_code == 200:
								posts = response.json()['posts']

								# Set correct author
								found_author = author
								try:
									following_status = True if author_id in user.remote_following_uuid else False
								except:
									following_status = False
								
								try:
									follower_status = True if author_id in user.remote_followers_uuid else False
								except:
									follower_status = False


	if following_status or follower_status:
		follow_status = True
	else:
		follow_status = False
	# A and B are friends <=> A follows B and B follows A
	friend_status = follower_status and following_status
	if request.method == "GET":
		return render(request, 'profile/view_profile.html', {'author': found_author, 'posts': posts, 'friend_status': friend_status, 'following_status': following_status,
					'follower_status': follower_status, 'follow_status': follow_status, 'local': local})

def follow(request, author_id):
	sender = request.user.author
	TEAM3_URL = "https://team3-socialdistribution.herokuapp.com/"
	local = True
	try:
		receiver = Author.objects.get(id=author_id)
	except:
		local = False
		for connection in Connection.objects.all():
			if connection.name == "localhost":
				temp = sender.remote_following_uuid
				if temp:
					if author_id not in temp:
						sender.remote_following_uuid += f' {author_id}'
				else:
					sender.remote_following_uuid = author_id
				sender.save()
			else:
				url = connection.url + 'service/authors/'
				response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
				if response.status_code == 200:
					for author in response.json()['items']:
						# Found a match!
						if author_id == author['id']:
							receiver = author

							post_data = {}
							post_data['type'] = 'follow'
							post_data['summary'] = sender.displayName + ' wants to follow ' + receiver['displayName']
							post_data['actor'] = {
								'type': 'author',\
								'id': f"{TEAM3_URL}author/{sender.id}",\
								'authorID': str(sender.id),\
								'host': TEAM3_URL,\
								'displayName': sender.displayName,\
								'github': f"https://github.com/{sender.github}/"\
							}
							post_data['object'] = receiver

							# Send request to remote
							url = connection.url + 'service/author/' + receiver['id'] + '/inbox/'
							post_response = requests.post(url, json.dumps(post_data), headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
							if post_response.status_code in [200, 304, '', None]:
								temp = sender.remote_following_uuid
								if temp:
									if author_id not in temp:
										sender.remote_following_uuid += f' {author_id}'
								else:
									sender.remote_following_uuid = author_id
								sender.save()
							print(post_response.status_code)

	if local:
		# Create friend request
		friend_request = FriendRequest(sender=sender, receiver=receiver)

		# Add to database
		friend_request.save()

		# Send friend request object to inbox
		receiver.inbox.follow_items.add(friend_request)

		# Add the receiver to the sender's following list
		sender.following.add(receiver)
		receiver.followers.add(sender)

	return redirect('Profile:view_profile', author_id)

def unfollow(request, author_id):
	user = Author.objects.get(user__username=request.user.username)
	try:
		# Local
		user_following = Author.objects.get(id=author_id)


		# Remove connection

		# ToDo: what other models must be updated? See email
		user.following.remove(user_following)
		user_following.followers.remove(user)
	
	except:
		# Remote
		remote_following_list = user.remote_following_uuid.strip().split(" ")
		remote_following_list.remove(author_id)
		user.remote_following_uuid = " ".join(remote_following_list)
		user.save()

	return redirect('Profile:view_profile', author_id)



def like_post(request, author_id, post_id):
	current_user = request.user

	post = Post.objects.filter(id=post_id, author__id=author_id).get()
	if post:
		# Local post
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

			# Add to inbox
			content_author = Author.objects.get(id=author_id)
			content_author.inbox.post_like_items.add(like_instance)

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
	else:
		# Remote post

		# See if we have already liked this post
		# host = None
		# for connection in Connection.objects.all():
		# 	url = connection.url() + f'/service/author/{author_id}/post/{post_id}/likes/'
		# 	response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
		# 	likes = response.json()
		# 	print(likes)
		# 	liked = False
		# 	for like in likes['likes']:
		# 		if like['author']['id'] == current_user.id:
		# 			host = like['author']['host']
		# 			liked = True
		# 			break

		# if not liked:
		# 	url = host + f'/service/author/{author_id}/inbox/'
		# 	post_data = {}
		# 	post_data['Summary'] = current_user.author.displayName + ' likes your post'
		# 	post_data['type'] = 'Like'
		# 	post_data['actor'] = AuthorSerializer(current_user.author).data
		# 	post_data['object'] = host + f'/author/{author_id}/posts/{post_id}/'
		# 	print(post_data)

		return redirect('Profile:view_post', author_id, post_id)




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
	following = author.following.all()

	# Friends posts contain all the post from the people you follow
	friend_posts = author.inbox.post_items.all()
	posts = private_posts | friend_posts

	# Grab friend requests from inbox
	friend_requests = author.inbox.follow_items.all()

	# Grab likes from inbox
	likes = author.inbox.post_like_items.all()

	if request.method == "GET":
		inbox_option = request.GET.get("inbox_option")
		if inbox_option == "All":
			posts = posts.order_by('-timestamp')
		elif inbox_option == "Cleared":
			posts = author.inbox.post_items_cleared.all().order_by('-timestamp')
			friend_requests = author.inbox.follow_items_cleared.all()
			likes = author.inbox.post_like_items_cleared.all()
		else:
			posts = posts.difference(author.inbox.post_items_cleared.all()).order_by('-timestamp')
			friend_requests = friend_requests.difference(author.inbox.follow_items_cleared.all())
			likes = likes.difference(author.inbox.post_like_items_cleared.all())

		return render(request, 'profile/inbox.html', {'posts':posts, 'author':author, 'friend_requests': friend_requests, 'likes': likes})
	elif request.method == "POST":
		if "clear_signal" in request.POST:
			author.inbox.post_items_cleared.add(*posts)
			author.inbox.follow_items_cleared.add(*friend_requests)
			author.inbox.post_like_items_cleared.add(*likes)

		posts = posts.difference(author.inbox.post_items_cleared.all()).order_by('-timestamp')
		friend_requests = friend_requests.difference(author.inbox.follow_items_cleared.all())
		likes = likes.difference(author.inbox.post_like_items_cleared.all())

		return render(request, 'profile/inbox.html', {'posts': posts, 'author': author, 'friend_requests': friend_requests, 'likes': likes})
