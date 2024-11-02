from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers

def add_user(request):
    required_keys = ["name", "email", "password", "role", "mobileno", "username"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                "Name, email, and password are required fields.")

        if User.objects.filter(email=data['email']).exists():
            return HttpResponseBadRequest(json.dumps({"Error":"A user with this email already exists."}),content_type='application/json')
    
        if User.objects.filter(mobileno=data['mobileno']).exists():
            return HttpResponseBadRequest(json.dumps({"Error":"A user with this mobile no. already exists."}),content_type='application/json')

    

        touroperator = Touroperator.objects.filter(id = data['tour_operator_id'])[0]
        user = User(tour_operator_id=touroperator,
                    name=data['name'],
                    email=data['email'],
                    password_hash=make_password(data['password']),
                    role=data['role'],
                    is_active=data['is_active'],
                    mobileno=data['mobileno'])
                    #username=data['username'])

        user.save()
        data = serializers.serialize('json', [user,])
        return HttpResponse(data,content_type='application/json')

def get_users(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        user_id = None
        tour_operator_id  = None
        if 'user_id' in data:
            user_id = data['user_id']
        
        if 'tour_operator_id' in data:
            tour_operator_id = data['tour_operator_id']

        if user_id is not None:
            users = User.objects.filter(id =user_id)
        elif tour_operator_id  is not None:
            users = User.objects.filter(tour_operator_id =tour_operator_id)
        else:
            users = User.objects.all()
        
        for user in users:
            user_data = serializers.serialize('json', [user,])
            result.append(json.loads(user_data)[0])
        

        return HttpResponse(json.dumps(result),content_type='application/json')

def validate_user(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        user_id = None
        tour_operator_id  = None
        if 'username' not in data:
            return HttpResponse(json.dumps({"error":"username and password are required field."}),content_type='application/json')

        if 'password' not in data:
            return HttpResponse(json.dumps({"error":"username and password are required field."}),content_type='application/json')


        username = data['username']
        password = data['password']
        
        
        
        user = User.objects.filter(username =username).first()
        if not user:
            return HttpResponse(json.dumps({"error":"username or password is invalid"}),content_type='application/json')
        else:
            if check_password(password,user.password_hash):
                user_data = serializers.serialize('json', [user,])

                return HttpResponse(user_data,content_type='application/json')
            else:
                return HttpResponse(json.dumps({"error":"username or password is invalid"}),content_type='application/json')