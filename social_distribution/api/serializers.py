from rest_framework import serializers

from Profile.models import Author, Post, Comment, PostLike, CommentLike
from Search.models import FriendRequest

from django.contrib.auth.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('type', 'id', 'displayName', 'bio', 'location', 'url', 'birth_date', 'github', 'host')

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description',
                    'content_type', 'content', 'author', 'comments', 'categories', 'timestamp',
                    'visibility', 'unlisted')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        data['comments'] = CommentSerializer(Comment.objects.filter(id__in=data['comments']), many=True).data
        return data

    # https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
    def perform_create(self, serializer):
        author = Author.objects.get(user__username=self.request.user.username)
        serializer.save(author=author)

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
        fields = ('type', 'author', 'content', 'timestamp', 'id')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        return data


class LikeSerializer(serializers.ModelSerializer):
    summary = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=200)
    author = AuthorSerializer(many=False)
    object = serializers.CharField(max_length=500)

    def create(self, validated_data):
        if validated_data['type'] == 'post':
            return PostLike(**validated_data)
        elif validated_data['type'] == 'comment':
            return CommentLike(**validated_data)

    def update(self, instance, validated_data):
        instance.summary = validated_data.get('summary', instance.summary)
        instance.author = validated_data.get('author', instance.author)
        instance.object = validated_data.get('object', instance.object)
        instance.save()
        return instance

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        # data['summary'] = " likes your comment"
        return data

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ('summary', 'type', 'author', 'object')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        return data


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ('summary', 'type', 'author', 'object')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        return data
