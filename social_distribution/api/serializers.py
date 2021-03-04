from rest_framework import serializers

from Profile.models import Author, Post

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
                    'published', 'visibility', 'unlisted')
