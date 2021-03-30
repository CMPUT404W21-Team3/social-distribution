from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
import requests
import json

from .forms import SearchForm
from .models import FriendRequest

from Profile.models import Author
from api.models import Connection

# Create your views here.
def results(request):
    query = request.POST.get('query', '')
    authors = Author.objects.filter(user__username__contains=query)

    remote_authors = []

    for connection in Connection.objects.all():
        url = connection.url + 'service/authors'
        response = requests.get(url, headers={"mode":"no-cors"}, body={"username": "CitrusNetwork", "password": "oranges"})
        for author in response.json()['items']:
            remote_authors.append(author)

    authors = list(authors)
    authors += remote_authors

    return render(request, 'results.html', {'query': query, 'authors': authors})
