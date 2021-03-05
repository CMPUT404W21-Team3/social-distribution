from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Author, Post

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('bio', 'location', 'birth_date', 'github')

class SignUpForm(UserCreationForm):
    #birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', ) #could add birth-date field later on.

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('title', 'source', 'origin', 'content_type', 'description', 'content', 'categories', 'visibility')
