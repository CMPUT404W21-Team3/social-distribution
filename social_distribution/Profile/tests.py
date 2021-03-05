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
        self.assertEqual(response.status_code, 200, "Correct author ID and post ID should return 200")
        self.assertEqual(response.context['post'], self.post1, msg='Incorrect post displayed')

    def test_wrong_author(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':self.author2.id, 'post_id':self.post1.id}))
        self.assertEqual(response.status_code, 404, "Author ID for wrong owner should return 404")

    def test_random_post_uuid(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':self.author1.id, 'post_id':uuid.uuid4()}))
        self.assertEqual(response.status_code, 404, "Incorrent post ID should return 404")

    def test_random_author_and_post_uuid(self):
        self.setup()
        response = self.client.get(reverse('Profile:view_post', kwargs={'author_id':uuid.uuid4(), 'post_id':uuid.uuid4()}))
        self.assertEqual(response.status_code, 404, "Incorrent author ID and post ID should return 404")


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
        self.assertEqual(response.status_code, 200, "Correct author ID should return 200")
        self.assertEqual(set(response.context['posts']), set([self.post1, self.post2, self.post3]), "Wrong posts returned")


class TestEditPost(TestCase):
    def setup(self):
        self.client = Client()
        self.user1 = User.objects.create_user('test1', 'test1@gmail.com', 'pwd', is_active=True)
        self.user2 = User.objects.create_user('test2', 'test2@gmail.com', 'pwd', is_active=True)
        self.author1 = self.user1.author
        self.author2 = self.user2.author
        self.post1 = Post.objects.create(title='Test Post 1', content="Test content 1", author=self.author1)
        self.post2 = Post.objects.create(title='Test Post 2', content="Test content 2", author=self.author2)

    # Login as test1
    def login(self):
        self.client.force_login(self.user1)

    def test_edit_post(self):
        self.setup()
        self.login()
        response = self.client.post(
            reverse("Profile:edit_post", kwargs={'post_id':self.post1.id}), 
            data={
                "title":self.post1.title, 
                "content_type": self.post1.content_type,
                "content":"Test edited content",
                "visibility": self.post1.visibility
            }
        )
        
        self.assertRedirects(
            response=response, 
            expected_url=reverse('Profile:view_post', kwargs={'author_id':self.author1.id, 'post_id':self.post1.id}), 
            status_code=302, 
            target_status_code=200, # Target status code of redirected page
            msg_prefix="Should redirect to edited post's page"
        )

        self.post1.refresh_from_db()
        self.assertEqual(self.post1.content, "Test edited content", "Content should have been edited")

    def test_edit_post_not_owner(self):
        self.setup()
        self.login()
        response = self.client.post(reverse(
            "Profile:edit_post", kwargs={'post_id':self.post2.id}), 
            data={
                "title":self.post2.title, 
                "content_type": self.post2.content_type,
                "content":"Test edited content",
                "visibility": self.post2.visibility
            }
        )
        self.assertEqual(response.status_code, 403, "Should be forbidden")
        self.post2.refresh_from_db()
        self.assertEqual(self.post2.content, "Test content 2")


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
            reverse("Profile:new_post"),
            data={
                "title":"New Post Title",
                "content_type":"text/plain",
                "content":"New post content",
                "visibility":"PUBLIC"
            }
        )
        self.assertEqual(response.status_code, 302)

        post = Post.objects.all()[0]
        self.assertEqual(post.title, "New Post Title")
        self.assertEqual(post.content, "New post content")
        self.assertEqual(post.author, self.author1)