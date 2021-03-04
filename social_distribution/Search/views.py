from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .forms import SearchForm
from .models import FriendRequest

from Profile.models import Author

# Create your views here.
def results(request):
    query = request.POST.get('query', '')
    users = User.objects.filter(username__contains=query)
    return render(request, 'results.html', {'query': query, 'users': users})
