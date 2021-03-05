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

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        data['comments'] = CommentSerializer(Comment.objects.filter(id__in=data['comments']), many=True).data
        return data

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('type', 'summary', 'sender', 'receiver')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = AuthorSerializer(Author.objects.get(pk=data['sender'])).data
        data['receiver'] = AuthorSerializer(Author.objects.get(pk=data['receiver'])).data
        return data

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('type', 'author', 'content', 'content_type', 'timestamp', 'id')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        return data
