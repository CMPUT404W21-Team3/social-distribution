from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from rest_framework import viewsets

from .serializers import ProfileSerializer
from Profile.models import Profile


# Create your views here.
def get_profile(request, id):
    """
    Retrieve a profile.
    """
    try:
        profile = Profile.objects.get(user_id=id)
    except Profile.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return JsonResponse(serializer.data)
