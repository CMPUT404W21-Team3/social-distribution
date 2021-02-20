from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .forms import SearchForm
from .models import FriendRequest

# Create your views here.
def results(request):
    query = request.POST.get('query', '')
    users = User.objects.filter(username__contains=query)
    return render(request, 'results.html', {'query': query, 'users': users})

# TODO: check if request has already been made
def friend_request(request):
    # Create request object
    receiver = request.POST.get('receiver', '')
    friend_request = FriendRequest(type='follow', sender=request.user.username, receiver=receiver)

    # Add to database
    friend_request.save()

    # Todo: Add the receiver to the sender's following list

    # Bad practice, should try to find a way around this
    # Other methods are very buggy, will fix later
    query = request.POST.get('query', '')
    users = User.objects.filter(username__contains=query)

    # TODO: doesn't update url in browser
    return render(request, 'results.html', {'query': query, 'users': users})
