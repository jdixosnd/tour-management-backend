from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
import json
from ..models import Customer, Touroperator, User
from django.core.exceptions import ValidationError
from django.core import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


def add_customer(request):
    """
    Add a new customer to the system.
    Required fields: tour_operator_id, name, phone
    Optional fields: email, address
    """
    required_keys = ["tour_operator_id", "name", "phone"]

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            missing_keys = set(required_keys) - data.keys()
            
            # Check for missing keys
            if missing_keys:
                return JsonResponse({
                    "code": 400,
                    "message": f"Missing required fields: {', '.join(missing_keys)}"
                }, status=400)

            # Validate tour operator exists
            try:
                touroperator = Touroperator.objects.get(uuid=data['tour_operator_id'])
            except Touroperator.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Tour operator not found"
                }, status=404)

            # Check if customer with same phone already exists for this tour operator
            if Customer.objects.filter(
                tour_operator=touroperator,
                phone=data['phone']
            ).exists():
                return JsonResponse({
                    "code": 409,
                    "message": "A customer with this phone number already exists for this tour operator"
                }, status=409)

            # Create customer
            customer = Customer(
                tour_operator=touroperator,
                name=data['name'],
                phone=data['phone'],
                email=data.get('email'),
                address=data.get('address')
            )
            
            customer.save()
            
            return JsonResponse({
                "code": 200,
                "message": "Customer added successfully",
                "customer_id": str(customer.uuid),
                "data": {
                    "id": str(customer.uuid),
                    "tour_operator_id": str(customer.tour_operator.uuid),
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "created_at": str(customer.created_at)
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({
                "code": 400,
                "message": "Invalid JSON format"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "code": 500,
                "message": f"Something went wrong: {str(e)}"
            }, status=500)


def get_customers(request):
    """
    Get customers with optional filtering.
    Required: tour_operator_id
    Optional filters: customer_id, phone, email, name
    Supports pagination.
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode("utf-8"))

            # tour_operator_id is required
            if 'tour_operator_id' not in data or not data['tour_operator_id']:
                return JsonResponse({
                    "code": 400,
                    "message": "tour_operator_id is required"
                }, status=400)

            # Validate tour operator exists
            try:
                touroperator = Touroperator.objects.get(uuid=data['tour_operator_id'])
            except Touroperator.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Tour operator not found"
                }, status=404)

            # Start with customers filtered by tour operator (data isolation)
            customers = Customer.objects.filter(tour_operator__uuid=data['tour_operator_id'])

            # Apply additional filters if provided
            if 'customer_id' in data and data['customer_id']:
                customers = customers.filter(uuid=data['customer_id'])

            if 'phone' in data and data['phone']:
                customers = customers.filter(phone__icontains=data['phone'])

            if 'email' in data and data['email']:
                customers = customers.filter(email__icontains=data['email'])

            if 'name' in data and data['name']:
                customers = customers.filter(name__icontains=data['name'])
            
            # Order by created_at descending
            customers = customers.order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = data.get('page_size', 10)
            
            # Convert request to DRF Request for pagination
            drf_request = Request(request)
            paginated_customers = paginator.paginate_queryset(customers, drf_request)
            
            # Build result
            result = []
            for customer in paginated_customers:
                result.append({
                    "id": str(customer.uuid),
                    "tour_operator_id": str(customer.tour_operator.uuid) if customer.tour_operator else None,
                    "tour_operator_name": customer.tour_operator.name if customer.tour_operator else None,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "created_at": str(customer.created_at)
                })
            
            return JsonResponse({
                "code": 200,
                "data": result,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            "code": 400,
            "message": "Invalid JSON format"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"Something went wrong: {str(e)}"
        }, status=500)


def update_customer(request):
    """
    Update an existing customer.
    Required fields: customer_id
    Optional fields: name, phone, email, address
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            if 'customer_id' not in data:
                return JsonResponse({
                    "code": 400,
                    "message": "customer_id is required"
                }, status=400)
            
            # Get customer
            try:
                customer = Customer.objects.get(uuid=data['customer_id'])
            except Customer.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Customer not found"
                }, status=404)
            
            # Check if phone is being updated and if it conflicts with another customer
            if 'phone' in data and data['phone'] != customer.phone:
                if Customer.objects.filter(
                    tour_operator=customer.tour_operator,
                    phone=data['phone']
                ).exclude(uuid=customer.uuid).exists():
                    return JsonResponse({
                        "code": 409,
                        "message": "A customer with this phone number already exists for this tour operator"
                    }, status=409)
            
            # Update fields if provided
            if 'name' in data:
                customer.name = data['name']
            if 'phone' in data:
                customer.phone = data['phone']
            if 'email' in data:
                customer.email = data['email']
            if 'address' in data:
                customer.address = data['address']
            
            customer.save()
            
            return JsonResponse({
                "code": 200,
                "message": "Customer updated successfully",
                "data": {
                    "id": str(customer.uuid),
                    "tour_operator_id": str(customer.tour_operator.uuid) if customer.tour_operator else None,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "created_at": str(customer.created_at)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                "code": 400,
                "message": "Invalid JSON format"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "code": 500,
                "message": f"Something went wrong: {str(e)}"
            }, status=500)


def delete_customer(request):
    """
    Delete a customer.
    Required fields: customer_id
    Note: This will fail if customer is referenced in leads or transactions due to PROTECT constraint.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            if 'customer_id' not in data:
                return JsonResponse({
                    "code": 400,
                    "message": "customer_id is required"
                }, status=400)
            
            # Get customer
            try:
                customer = Customer.objects.get(uuid=data['customer_id'])
            except Customer.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Customer not found"
                }, status=404)
            
            customer_name = customer.name
            customer.delete()
            
            return JsonResponse({
                "code": 200,
                "message": f"Customer '{customer_name}' deleted successfully"
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                "code": 400,
                "message": "Invalid JSON format"
            }, status=400)
        except Exception as e:
            # Handle PROTECT constraint violations
            if 'PROTECT' in str(e) or 'foreign key constraint' in str(e).lower():
                return JsonResponse({
                    "code": 409,
                    "message": "Cannot delete customer as it is referenced in leads or transactions"
                }, status=409)
            return JsonResponse({
                "code": 500,
                "message": f"Something went wrong: {str(e)}"
            }, status=500)

