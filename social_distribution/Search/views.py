from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .forms import SearchForm
from .models import FriendRequest

from Profile.models import Author

# Create your views here.
def results(request):
    query = request.POST.get('query', '')
    # Local authors
    local_authors = Author.objects.filter(user__username__contains=query)

    authors = local_authors
    return render(request, 'results.html', {'query': query, 'authors': authors})
