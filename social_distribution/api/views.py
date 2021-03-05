from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response

from .serializers import AuthorSerializer, PostSerializer, CommentSerializer
from Profile.models import Author, Post, Comment

# https://www.django-rest-framework.org/tutorial/1-serialization/ - was consulted in writing code

# Create your views here.
@api_view(['GET', 'POST'])
def get_author(request, author_id):
    """
    Retrieve or update an author.
    """
    try:
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    elif request.method == 'POST':
        # TODO: add authentication
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
def get_post(request, author_id, post_id):
    """
    Create, retrieve, update or delete a post.
    """

    # Create new post
    if request.method == 'PUT':
        # See if credentials supplied
        if 'password' not in request.data or 'username' not in request.data:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Log in with those credentials
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if author_id == str(Author.objects.get(user__username=username).id):
                    author = Author.objects.get(id=author_id)
                    instance = Post.objects.create(author=author, id=post_id)
                    serializer = PostSerializer(instance, data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)


        return Response(status=status.HTTP_401_UNAUTHORIZED)

    # Else, do something with existing post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        if post.visibility != 'PUBLIC':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if 'password' not in request.data or 'username' not in request.data:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Log in with those credentials
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if str(Author.objects.get(user__username=username).id) == str(Post.objects.get(id=post_id).author.id):
                    print(author_id)
                    print(Post.objects.get(id=post_id).author.id)
                    post.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def get_posts(request, author_id):
    """
    Get posts from an author or create a post and auto generate an id for it.
    """

    if request.method == 'GET':
        posts = Post.objects.filter(author__id=author_id, visibility='PUBLIC', unlisted=False).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        author = Author.objects.get(id=author_id)
        instance = Post.objects.create(author=author)
        serializer = PostSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_followers(request, author_id):
    if request.method == 'GET':
        followers = Author.objects.get(id=author_id).followers.all()
        serializer = AuthorSerializer(followers, many=True)
        return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def get_follower(request, author_id, follower_id):
    """
    Retrieve or delete follower of author, or add user as a follower
    """

    try:
        author = Author.objects.get(id=author_id)
        follower = Author.objects.get(id=follower_id)
    except Author.DoesNotExist:
        return HttpResponse(status=404)

    # Add as follower
    if request.method == 'PUT':
        if 'password' not in request.data or 'username' not in request.data:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Log in with those credentials
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if follower_id == str(Author.objects.get(user__username=username).id):
                    author.followers.add(follower)
                    follower.following.add(author)
                    return HttpResponse(status=200)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        if follower in author.followers.all():
            serializer = AuthorSerializer(follower)
            return Response(serializer.data)
        # Not a follower
        return HttpResponse(status=404)

    elif request.method == 'DELETE':
        # TODO: add authentication
        if 'password' not in request.data or 'username' not in request.data:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Log in with those credentials
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if follower_id == str(Author.objects.get(user__username=username).id):
                    author.followers.remove(follower)
                    follower.following.remove(author)
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def get_comments(request, author_id, post_id):
    """
    Get comments from a post or create a post and auto generate an id for it.
    """

    if request.method == 'GET':
        post = Post.objects.get(id=post_id)

        if post.visibility != 'PUBLIC':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # TODO: add authentication
        if request.data['type'] == "comment":
            author = Author.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)

            instance = Comment.objects.create(author=author)
            post.comments.add(instance)

            serializer = CommentSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
