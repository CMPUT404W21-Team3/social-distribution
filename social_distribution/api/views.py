from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response

from .serializers import AuthorSerializer, PostSerializer
from Profile.models import Author, Post


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
        # TODO: add authentication1
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
    # Not working
    if request.method == 'PUT':
        # TODO: add authentication
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        # TODO: add authentication
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # TODO: add authentication
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        # TODO: add authentication
        # Not working
        serializer = PostSerializer(data=request.data)
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
    Create, retrieve or delete follower of author
    """
    # Create new follower
    if request.method == 'PUT':
        # TODO: add authentication
        pass

    try:
        author = Author.objects.get(id=author_id)
        follower = Author.objects.get(id=follower_id)
    except Author.DoesNotExist:
        return HttpResponse(status=404)

    # Do something with existing follower
    if request.method == 'GET':
        if follower in author.followers.all():
            serializer = AuthorSerializer(follower)
            return Response(serializer.data)
        # Not a follower
        return HttpResponse(status=404)

    elif request.method == 'DELETE':
        # TODO: add authentication
        author.followers.remove(follower)
        follower.following.remove(author)
        return Response(status=status.HTTP_204_NO_CONTENT)
