from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Post, Author
import uuid

class ViewPostTests(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.post1 = Post.objects.create(title='Test Post 1', author=self.author1)
        self.post2 = Post.objects.create(title='Test Post 2', author=self.author2)

    def test_correct(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':self.author1.id, 'post_id':self.post1.id}))
        self.assertEqual(response.status_code, 200, 'Correct author ID and post ID should return 200')
        self.assertEqual(response.context['post'], self.post1, msg='Incorrect post displayed')

    def test_wrong_author(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':self.author2.id, 'post_id':self.post1.id}))
        self.assertEqual(response.status_code, 404, 'Author ID for wrong owner should return 404')

    def test_random_post_uuid(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':self.author1.id, 'post_id':uuid.uuid4()}))
        self.assertEqual(response.status_code, 404, 'Incorrent post ID should return 404')

    def test_random_author_and_post_uuid(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':uuid.uuid4(), 'post_id':uuid.uuid4()}))
        self.assertEqual(response.status_code, 404, 'Incorrent author ID and post ID should return 404')


class PostListTest(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.post1 = Post.objects.create(title='Test Post 1', author=self.author1)
        self.post2 = Post.objects.create(title='Test Post 2', author=self.author1)
        self.post3 = Post.objects.create(title='Test Post 3', author=self.author1)
        self.post4 = Post.objects.create(title='Test Post 4', author=self.author2)
        self.post5 = Post.objects.create(title='Test Post 5', author=self.author2)

    # Login as test1
    def login(self):
        self.client.force_login(self.user1)

    def test_post_list(self):
        self.setup()
        self.login()
        response = self.client.get(reverse('Profile:view_posts', kwargs={'author_id':self.author1.id}))
        self.assertEqual(response.status_code, 200, 'Correct author ID should return 200')
        self.assertEqual(set(response.context['posts']), set([self.post1, self.post2, self.post3]), 'Wrong posts returned')


class TestEditPost(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.post1 = Post.objects.create(title='Test Post 1', content='Test content 1', author=self.author1)
        self.post2 = Post.objects.create(title='Test Post 2', content='Test content 2', author=self.author2)

    # Login as test1
    def login(self):
        self.client.force_login(self.user1)

    def test_edit_post(self):
        self.setup()
        self.login()
        response = self.client.post(
            reverse('Profile:edit_post', kwargs={'post_id':self.post1.id}), 
            data={
                'title':self.post1.title, 
                'content_type': self.post1.content_type,
                'content':'Test edited content',
                'visibility': self.post1.visibility
            }
        )
        
        self.assertRedirects(
            response=response, 
            expected_url=reverse('Profile:view_post', kwargs={'author_id':self.author1.id, 'post_id':self.post1.id}), 
            status_code=302, 
            target_status_code=200, # Target status code of redirected page
            msg_prefix='Should redirect to edited post\'s page'
        )

        self.post1.refresh_from_db()
        self.assertEqual(self.post1.content, 'Test edited content', 'Content should have been edited')

    def test_edit_post_not_owner(self):
        self.setup()
        self.login()
        response = self.client.post(reverse(
            'Profile:edit_post', kwargs={'post_id':self.post2.id}), 
            data={
                'title':self.post2.title, 
                'content_type': self.post2.content_type,
                'content':'Test edited content',
                'visibility': self.post2.visibility
            }
        )
        self.assertEqual(response.status_code, 403, 'Should be forbidden')
        self.post2.refresh_from_db()
        self.assertEqual(self.post2.content, 'Test content 2')


class TestNewPost(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
    
    def login(self):
        self.client.force_login(self.user1)
    
    def test_new_post(self):
        self.setup()
        self.login()

        response = self.client.post(
            reverse('Profile:new_post'),
            data={
                'title':'New Post Title',
                'content_type':'text/plain',
                'content':'New post content',
                'visibility':'PUBLIC'
            }
        )
        self.assertEqual(response.status_code, 302)

        post = Post.objects.all()[0]
        self.assertEqual(post.title, 'New Post Title')
        self.assertEqual(post.content, 'New post content')
        self.assertEqual(post.author, self.author1)

class TestDeletePost(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.post1 = Post.objects.create(title='Test Post 1', content='Test content 1', author=self.author1)
        self.post2 = Post.objects.create(title='Test Post 2', content='Test content 2', author=self.author1)
        self.post3 = Post.objects.create(title='Test Post 3', content='Test content 3', author=self.author2)

    def login(self):
        self.client.force_login(self.user1)

    def test_delete_post(self):
        self.setup()
        self.login()
        response = self.client.get(reverse('Profile:delete_post', kwargs={'post_id':self.post1.id}))
        self.assertEqual(set(self.author1.posts.all()), set([self.post2]), msg='Post 1 should have been deleted and the queryset should only contain post 2')
        self.assertRedirects(
            response=response,
            expected_url=reverse('Profile:view_posts', kwargs={'author_id':self.author1.id}),
            status_code=302,
            target_status_code=200,
            msg_prefix='Should redirect to view_posts page'
        )

    def test_delete_not_owner(self):
        self.setup()
        self.login()
        
        # Try to delete post 3, which is owned by author2, logged in as author1
        response = self.client.get(reverse('Profile:delete_post', kwargs={'post_id':self.post3.id}))
        self.assertEqual(response.status_code, 403, 'Should return 403 Forbidden')
        self.assertEqual(set(self.author2.posts.all()), set([self.post3]), 'Post 3 should not have been deleted')

class TestFriendRequest(TestCase):
    def setup(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)

    def test_friend_request(self):
        self.setup()

        # Send a friend request to author2 loggin in as author1
        response = self.client1.get(reverse('Profile:friend_request', kwargs={'author_id':self.author2.id}))
        self.assertRedirects(
            response,
            expected_url=reverse('Profile:view_profile', kwargs={'author_id':self.author2.id}),
            status_code=302,
            target_status_code=200,
            msg_prefix='Should have been redirected to author2\'s profile page'
        )

        self.assertEqual(set(self.author2.followers.all()), set([self.author1]), 'author1 should be a follower of author2')
        self.assertEqual(set(self.author1.following.all()), set([self.author2]), 'author1 should be following author2')
        self.assertEqual(set(self.author1.friends.all()), set(), 'author1 and author2 should not be friends yet')
        self.assertEqual(set(self.author2.friends.all()), set(), 'author1 and author2 should not be friends yet')

        response = self.client2.get(reverse('Profile:friends'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['friend_requests'][0].sender, self.author1, 'Friend request from author1 should appear')

        response = self.client2.post(reverse('Profile:accept'), data={'sender':self.author1.user.username})
        self.assertRedirects(
            response,
            expected_url=reverse('Profile:friends'),
            status_code=302,
            target_status_code=200,
            msg_prefix='Should redirect to friends list page'
        )

        self.assertEqual((set(self.author1.friends.all())), set([self.author2]))
        self.assertEqual((set(self.author2.friends.all())), set([self.author1]))