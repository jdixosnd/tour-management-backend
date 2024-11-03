from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from django.db import models
from django.http import JsonResponse

def add_user(request):
    required_keys = ["name", "email", "password", "role", "mobileno"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+ " are required fields.")

        if User.objects.filter(email=data['email']).exists():
            return HttpResponseBadRequest(json.dumps({"Error":"A user with this email already exists."}),content_type='application/json')
    
        if User.objects.filter(mobileno=data['mobileno']).exists():
            return HttpResponseBadRequest(json.dumps({"Error":"A user with this mobile no. already exists."}),content_type='application/json')

      

        touroperator = Touroperator.objects.filter(id = data['tour_operator_id'])[0]
        total_active_users = User.objects.filter(tour_operator_id=data['tour_operator_id'],is_active=True).count()
        if total_active_users >= touroperator.get_max_users():
            return JsonResponse({
                "error": "Max active users exceeded.",
                "total_active_users":total_active_users
            }, status=400)
        else:
            user = User(tour_operator_id=touroperator,
                        name=data['name'],
                        email=data['email'],
                        password_hash=make_password(data['password']),
                        role=data['role'],
                        is_active=data['is_active'],
                        mobileno=data['mobileno'])
                        #username=data['username'])

            user.save()
            return JsonResponse({
                    "message": "User added successfully",
                    "user_id": user.id
                }, status=201)

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
            result.append({
                        "id": user.id,
                        "tour_operator_id":user.tour_operator_id.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                        "mobileno": user.mobileno,
                        "username": user.username,
                        "is_active":user.is_active
                    })        

        return HttpResponse(json.dumps(result),content_type='application/json')

def validate_user(request):
    """
    Validate a user based on email, mobileno, or username and password.
    Returns user data if valid and active, appropriate error messages otherwise.

    :param identifier: The email, mobileno, or username of the user
    :param password: The password of the user
    :return: A tuple (user, message)
    """
    # Attempt to retrieve the user based on email, mobile number, or username
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        try:
            identifier = data['identifier']
            password = data['password']
            user = User.objects.get(
                models.Q(email=identifier) | 
                models.Q(mobileno=identifier) | 
                models.Q(username=identifier)
            )
        except User.DoesNotExist:
            return HttpResponse(json.dumps({"message":"Invalid username/password.","code":400}),content_type='application/json')


        # Check if the user is active
        if not user.is_active:
            return HttpResponse(json.dumps({"message":"User is inactive.","code":400}),content_type='application/json')

        # Verify the password
        if check_password(password, user.password_hash):
            user_data = {
                        "id": user.id,
                        "tour_operator_id":user.tour_operator_id.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                        "mobileno": user.mobileno,
                        "username": user.username
                    }
                
            return HttpResponse(json.dumps({"user":user_data,"message":"User validated successfully.","code":200}),content_type='application/json')

        else:
            return HttpResponse(json.dumps({"error":"Invalid username/password","code":400}),content_type='application/json')
    
