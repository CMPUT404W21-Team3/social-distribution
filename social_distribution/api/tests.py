from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from uuid import uuid4

from .models import Connection
from Profile.models import Author, Post, Comment, Like, PostLike, CommentLike
from .serializers import AuthorSerializer

# https://www.django-rest-framework.org/api-guide/testing/

def setup_auth():
    return Connection(
        name="test",
        incoming_username = '1234',
        incoming_password = '5678'
    )

AUTH = ('Basic ' + b64encode(b'1234:5678').decode('ascii')) # https://stackoverflow.com/q/48434485


class AuthorsTest(APITestCase):
    def setup(self):
        self.conn = setup_auth()
        self.conn.save()
        self.client.credentials(HTTP_AUTHORIZATION=AUTH)
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)

    def test_no_auth(self):
        self.setup()
        self.client.credentials() # Remove credentials
        url = '/authors'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_all_authors(self):
        self.setup()
        url = '/authors'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('test1' in str(response.content) and 'test2' in str(response.content))

    def get_specific_author(self):
        self.setup()
        url = '/author/' + self.user1.author.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('test1' in str(response.content))
        self.assert_('test1' not in str(response.content))


class PostsTest(APITestCase):
    def setup(self):
        self.conn = setup_auth()
        self.conn.save()
        self.client.credentials(HTTP_AUTHORIZATION=AUTH)
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.post1 = Post.objects.create(title='Test Post 1', author=self.user1.author)
        self.post2 = Post.objects.create(title='Test Post 2', author=self.user2.author)

    def test_no_auth(self):
        self.setup()
        self.client.credentials() # Remove credentials
        url = '/posts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_all_posts(self):
        self.setup()
        url = '/posts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('Test Post 1' in str(response.content) and 'Test Post 2' in str(response.content))

    def test_get_specific_post(self):
        self.setup()
        url = '/author/' + str(self.post1.author.id) + '/posts/' + str(self.post1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('Test Post 1' in str(response.content))
        self.assert_('Test Post 2' not in str(response.content))


class CommentsTest(APITestCase):
    def setup(self):
        self.conn = setup_auth()
        self.conn.save()
        self.client.credentials(HTTP_AUTHORIZATION=AUTH)
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.post1 = Post.objects.create(title='Test Post 1', author=self.user1.author)
        self.post2 = Post.objects.create(title='Test Post 2', author=self.user2.author)

    def test_no_auth(self):
        self.setup()
        self.client.credentials() # Remove credentials
        url = '/author/' + str(self.post1.author.id) + '/posts/' + str(self.post1.id) + '/comments'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_comment(self):
        self.setup()
        url = '/author/' + str(self.post1.author.id) + '/posts/' + str(self.post1.id) + '/comments'
        post_data = {
            'type':'comment',
            'author':{
                'id':uuid4(),
                'displayName':'test3',
            },
            'comment':'Nice post!',
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 200)
        post1_comment = self.post1.comments.first()
        self.assertEqual(post1_comment.content, 'Nice post!')

    def test_get_comments(self):
        self.setup()
        self.comment1 = Comment(
            post = self.post1,
            author = AuthorSerializer(self.user1.author).data,
            content = "This is a comment",
        )
        self.comment1.save()
        url = '/author/' + str(self.post1.author.id) + '/posts/' + str(self.post1.id) + '/comments'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('This is a comment' in str(response.content))

class LikeTest(APITestCase):
    def setup(self):
        self.conn = setup_auth()
        self.conn.save()
        self.client.credentials(HTTP_AUTHORIZATION=AUTH)
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.post1 = Post.objects.create(title='Test Post 1', author=self.user1.author)
        self.post2 = Post.objects.create(title='Test Post 2', author=self.user2.author)

    def test_no_auth(self):
        self.setup()
        self.client.credentials() # Remove credentials
        url = '/author/' + str(self.post1.author.id) + '/inbox'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_like_post(self):
        self.setup()
        url = '/author/' + str(self.post1.author.id) + '/inbox'
        post_data = {
            'type':'like',
            'author':{
                'id':uuid4(),
                'displayName':'test3',
            },
            'postID':str(self.post1.id),
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 200)

        url = '/author/' + str(self.post1.author.id) + '/posts/' + str(self.post1.id) + '/likes'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assert_('test3' in str(response.content))


class FriendTest(APITestCase):
    def setup(self):
        self.conn = setup_auth()
        self.conn.save()
        self.client.credentials(HTTP_AUTHORIZATION=AUTH)
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)

    def remote_follow(self):
        self.setup()
        url = '/author/' + str(self.post1.author.id) + '/inbox'
        sender_id = uuid4()
        post_data = {
            'type':'follow',
            'sender':{
                'id':sender_id,
                'displayName':'test3',
            },
            'receiver':{
                'id':str(self.user1.author.id),
            },
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assert_(sender_id in self.user1.author.remote_followers)