from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from django.db import models
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

def add_tour_operator(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Validate required fields
            required_fields = ["name", "email"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

            # Parse and create new tour operator
            tour_operator = Touroperator.objects.create(
                name=data.get("name"),
                email=data.get("email"),
                phone_number=data.get("phone_number"),
                address=data.get("address"),
                max_users=data.get("max_users"),
                renewal_date=parse_datetime(data.get("renewal_date")) if data.get("renewal_date") else None,
                account_life_months=data.get("account_life_months"),
            )

            # Return success response with the new tour operator's ID
            return JsonResponse({
                "message": "Tour operator added successfully",
                "tour_operator_id": tour_operator.id
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
def get_tour_operators(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        tour_operator_id = data.get('tour_operator_id')

        # Filter by tour_operator_id if provided, otherwise retrieve all
        if tour_operator_id is not None:
            tour_operators = Touroperator.objects.filter(id=tour_operator_id)
        else:
            tour_operators = Touroperator.objects.all()
        
        # Format the tour operator data
        for tour_operator in tour_operators:
            result.append({
                "id": tour_operator.id,
                "name": tour_operator.name,
                "email": tour_operator.email,
                "phone_number": tour_operator.phone_number,
                "address": tour_operator.address,
                "max_users": tour_operator.get_max_users(),
                "renewal_date": str(tour_operator.renewal_date),
                "account_life_months": tour_operator.get_account_life_months(),
                "created_at": str(tour_operator.created_at)
            })

        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(status=405)  # Method Not Allowed if not POST