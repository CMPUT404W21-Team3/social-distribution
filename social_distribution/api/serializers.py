from rest_framework import serializers

from Profile.models import Author, Post, Comment
from Search.models import FriendRequest

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('type', 'id', 'user_name', 'bio', 'location', 'birth_date', 'github')

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description',
                    'content_type', 'content', 'author', 'categories', 'comments_count',
                    'comments_page_size', 'comments_first_page', 'comments', 'timestamp',
                    'visibility', 'unlisted')

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('type', 'summary', 'sender', 'receiver')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('type', 'author', 'content', 'content_type', 'timestamp', 'id')
