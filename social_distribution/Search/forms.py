from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Search

class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)

    class Meta:
        model = Search
