from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
import requests
import json

from .forms import SearchForm
from .models import FriendRequest

from Profile.models import Author
from api.models import Connection

DEFAULT_HEADERS = {'Referer': 'https://team3-socialdistribution.herokuapp.com/', 'Mode': 'no-cors'}

# Create your views here.
def results(request):
    query = request.POST.get('query', '')
    authors = Author.objects.filter(user__username__contains=query)

    authors = list(authors)

    for connection in Connection.objects.all():
        url = connection.url + 'service/authors'
        response = requests.get(url, headers=DEFAULT_HEADERS, auth=(connection.outgoing_username, connection.outgoing_password))
        if response.status_code == 200:
            for author in response.json()['items']:
                if query in author['displayName']:
                    authors.append(author)

    return render(request, 'results.html', {'query': query, 'authors': authors})
