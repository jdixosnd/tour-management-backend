from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
import json
from .models import User, Touroperator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers

class ApplicationNameParser(APIView):

    def __init__(self):
        print("Obligation Management API Initiated.")

    def get(self, request):
        return HttpResponse("Obligation Management Service Up and Running")

    def put(self, request):
        return HttpResponse("Obligation Management Service Up and Running")

    def post(self, request):
        return HttpResponse("Obligation Management Service Up and Running")




def probe(request):
    return HttpResponse("success")
