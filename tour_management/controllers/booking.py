"""
Booking (Transaction) Controller
Handles booking creation and management from Leads
"""
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from ..models import (
    Customer, Destination, Touroperator, User,
    Transaction, TransactionItineraryItem, 
    Hotel, Cardealer, Lead, LeadPackage
)
import json
from decimal import Decimal


def add_booking(request):
    """
    Create a new booking (transaction) from a Lead with customer's selected options.
    
    Request Body:
    {
        "lead_id": 3,
        "created_by": 1,
        "package_snapshot": {
            "name": "Kerala Delight",
            "description": "...",
            "type": "leisure",
            "pax_size": 4,
            "no_of_days": 5,
            "inclusions": [...],
            "exclusions": [...],
            "amenities": [...],
            "policies": [...],
            "images": [...]
        },
        "itinerary_selections": [
            {
                "day": 1,
                "title": "Arrival in Kochi",
                "description": "...",
                "selected_hotel_id": 4,
                "selected_car_dealer_id": 2,
                "activities": [...]
            }
        ],
        "base_amount": 70000.00,
        "discount_amount": 5000.00,
        "taxes": 3500.00,
        "final_amount": 68500.00,
        "amount_paid": 20000.00,
        "amount_due": 48500.00,
        "travel_start_date": "2025-12-01",
        "travel_end_date": "2025-12-05",
        "booking_status": "confirmed",
        "payment_status": "partial",
        "booking_notes": "Customer requested early check-in"
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        
        # Required fields
        required_fields = ["lead_id", "created_by", "itinerary_selections", "final_amount"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)
        
        with transaction.atomic():
            # Get and validate lead
            try:
                lead = Lead.objects.select_related('customer', 'tour_operator').get(id=data['lead_id'])
            except Lead.DoesNotExist:
                return JsonResponse({"error": f"Lead with id {data['lead_id']} not found"}, status=404)

            # Get lead package to access destination
            try:
                lead_package = LeadPackage.objects.select_related('destination').get(lead=lead)
            except LeadPackage.DoesNotExist:
                return JsonResponse({"error": f"Lead package not found for lead {data['lead_id']}"}, status=404)

            # Get created_by user
            try:
                created_by = User.objects.get(id=data['created_by'])
            except User.DoesNotExist:
                return JsonResponse({"error": f"User with id {data['created_by']} not found"}, status=404)

            # Get package snapshot from request or lead
            package_snapshot = data.get('package_snapshot', {})

            # Create Transaction
            booking = Transaction.objects.create(
                lead=lead,
                customer=lead.customer,
                tour_operator=lead.tour_operator,
                created_by=created_by,
                destination=lead_package.destination,
                
                # Package snapshot
                package_name=package_snapshot.get('name', ''),
                package_description=package_snapshot.get('description', ''),
                package_type=package_snapshot.get('type', ''),
                pax_size=package_snapshot.get('pax_size'),
                no_of_days=package_snapshot.get('no_of_days'),
                package_inclusions=package_snapshot.get('inclusions', []),
                package_exclusions=package_snapshot.get('exclusions', []),
                package_amenities=package_snapshot.get('amenities', []),
                package_policies=package_snapshot.get('policies', []),
                package_images=package_snapshot.get('images', []),
                
                # Financial details
                base_amount=Decimal(str(data.get('base_amount', 0))),
                discount_amount=Decimal(str(data.get('discount_amount', 0))),
                taxes=Decimal(str(data.get('taxes', 0))),
                final_amount=Decimal(str(data['final_amount'])),
                amount_paid=Decimal(str(data.get('amount_paid', 0))),
                amount_due=Decimal(str(data.get('amount_due', 0))),
                
                # Booking details
                travel_start_date=data.get('travel_start_date'),
                travel_end_date=data.get('travel_end_date'),
                booking_status=data.get('booking_status', 'pending'),
                payment_status=data.get('payment_status', 'unpaid'),
                booking_notes=data.get('booking_notes', ''),
                
                # Set confirmed_at if status is confirmed
                confirmed_at=timezone.now() if data.get('booking_status') == 'confirmed' else None
            )
            
            # Create itinerary items with customer's selections
            for item_data in data['itinerary_selections']:
                # Get selected hotel if provided
                selected_hotel = None
                hotel_name = ''
                hotel_description = ''
                hotel_images = []
                
                if item_data.get('selected_hotel_id'):
                    try:
                        selected_hotel = Hotel.objects.get(id=item_data['selected_hotel_id'])
                        hotel_name = selected_hotel.name
                        hotel_description = selected_hotel.description or ''
                    except Hotel.DoesNotExist:
                        pass

                # Get selected transport if provided
                selected_car_dealer = None
                car_dealer_name = ''
                car_type = ''

                if item_data.get('selected_car_dealer_id'):
                    try:
                        selected_car_dealer = Cardealer.objects.get(id=item_data['selected_car_dealer_id'])
                        car_dealer_name = selected_car_dealer.name
                    except Cardealer.DoesNotExist:
                        pass

                # Create itinerary item
                TransactionItineraryItem.objects.create(
                    transaction=booking,
                    day=item_data['day'],
                    title=item_data.get('title', ''),
                    description=item_data.get('description', ''),

                    selected_hotel=selected_hotel,
                    hotel_name=hotel_name,
                    hotel_description=hotel_description,
                    hotel_images=item_data.get('hotel_images', []),

                    selected_car_dealer=selected_car_dealer,
                    car_dealer_name=car_dealer_name,
                    car_type=item_data.get('car_type', ''),

                    activities=item_data.get('activities', [])
                )

            return JsonResponse({
                "message": "Booking created successfully",
                "transaction_id": booking.id,
                "booking_id": booking.id
            }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_booking(request):
    """
    Get booking details by transaction_id.

    Request Body:
    {
        "transaction_id": 15
    }

    Response:
    {
        "transaction_id": 15,
        "lead_id": 3,
        "customer": {...},
        "package": {...},
        "itinerary": [...],
        "booking_status": "confirmed",
        "payment_status": "partial",
        "financial_details": {...},
        "travel_dates": {...},
        "timestamps": {...}
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        if 'transaction_id' not in data:
            return JsonResponse({"error": "Missing required field: transaction_id"}, status=400)

        try:
            booking = Transaction.objects.select_related(
                'customer', 'tour_operator', 'created_by'
            ).get(id=data['transaction_id'])
        except Transaction.DoesNotExist:
            return JsonResponse({"error": f"Booking with id {data['transaction_id']} not found"}, status=404)

        # Get itinerary items
        itinerary_items = TransactionItineraryItem.objects.filter(
            transaction=booking
        ).select_related('selected_hotel', 'selected_car_dealer').order_by('day')

        # Build response
        response_data = {
            "transaction_id": booking.id,
            "booking_id": booking.id,
            "lead_id": booking.lead.id if booking.lead else None,

            "customer": {
                "id": booking.customer.id,
                "name": booking.customer.name,
                "email": booking.customer.email,
                "phone": booking.customer.phone
            },

            "tour_operator": {
                "id": booking.tour_operator.id,
                "name": booking.tour_operator.name
            },

            "destination": {
                "id": booking.destination.id,
                "name": booking.destination.name
            } if booking.destination else None,

            "package": {
                "name": booking.package_name,
                "description": booking.package_description,
                "type": booking.package_type,
                "pax_size": booking.pax_size,
                "no_of_days": booking.no_of_days,
                "inclusions": booking.package_inclusions,
                "exclusions": booking.package_exclusions,
                "amenities": booking.package_amenities,
                "policies": booking.package_policies,
                "images": booking.package_images
            },

            "itinerary": [
                {
                    "day": item.day,
                    "title": item.title,
                    "description": item.description,
                    "hotel": {
                        "id": item.selected_hotel.id if item.selected_hotel else None,
                        "name": item.hotel_name,
                        "description": item.hotel_description,
                        "images": item.hotel_images
                    },
                    "transport": {
                        "id": item.selected_car_dealer.id if item.selected_car_dealer else None,
                        "name": item.car_dealer_name,
                        "car_type": item.car_type
                    },
                    "activities": item.activities
                }
                for item in itinerary_items
            ],

            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status,

            "financial_details": {
                "base_amount": float(booking.base_amount),
                "discount_amount": float(booking.discount_amount),
                "taxes": float(booking.taxes),
                "final_amount": float(booking.final_amount),
                "amount_paid": float(booking.amount_paid),
                "amount_due": float(booking.amount_due)
            },

            "travel_dates": {
                "start_date": booking.travel_start_date.isoformat() if booking.travel_start_date else None,
                "end_date": booking.travel_end_date.isoformat() if booking.travel_end_date else None
            },

            "booking_notes": booking.booking_notes,
            "cancellation_reason": booking.cancellation_reason,

            "timestamps": {
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
                "confirmed_at": booking.confirmed_at.isoformat() if booking.confirmed_at else None,
                "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None
            },

            "created_by": {
                "id": booking.created_by.id,
                "username": booking.created_by.username
            }
        }

        return JsonResponse(response_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_all_bookings(request):
    """
    Get all bookings with optional filters.

    Request Body:
    {
        "tour_operator": 1,  // Optional
        "customer_id": 5,  // Optional
        "booking_status": "confirmed",  // Optional
        "payment_status": "partial",  // Optional
        "destination_id": 2,  // Optional
        "from_date": "2025-01-01",  // Optional
        "to_date": "2025-12-31"  // Optional
    }

    Response:
    {
        "bookings": [
            {
                "transaction_id": 15,
                "customer_name": "John Doe",
                "package_name": "Kerala Delight",
                "booking_status": "confirmed",
                "payment_status": "partial",
                "final_amount": 68500.00,
                "amount_paid": 20000.00,
                "amount_due": 48500.00,
                "travel_start_date": "2025-12-01",
                "created_at": "2025-11-13T10:30:00Z"
            }
        ],
        "total_count": 1
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        # Start with all bookings
        bookings = Transaction.objects.select_related(
            'customer', 'tour_operator'
        ).all()

        # Apply filters
        if 'tour_operator' in data:
            bookings = bookings.filter(tour_operator_id=data['tour_operator'])

        if 'customer_id' in data:
            bookings = bookings.filter(customer_id=data['customer_id'])

        if 'booking_status' in data:
            bookings = bookings.filter(booking_status=data['booking_status'])

        if 'payment_status' in data:
            bookings = bookings.filter(payment_status=data['payment_status'])

        if 'destination_id' in data:
            bookings = bookings.filter(destination_id=data['destination_id'])

        if 'from_date' in data:
            bookings = bookings.filter(travel_start_date__gte=data['from_date'])

        if 'to_date' in data:
            bookings = bookings.filter(travel_start_date__lte=data['to_date'])

        # Order by created_at descending
        bookings = bookings.order_by('-created_at')

        # Build response
        bookings_list = [
            {
                "transaction_id": booking.id,
                "booking_id": booking.id,
                "lead_id": booking.lead.id if booking.lead else None,
                "customer_id": booking.customer.id,
                "customer_name": booking.customer.name,
                "customer_email": booking.customer.email,
                "package_name": booking.package_name,
                "destination": booking.destination.name if booking.destination else None,
                "booking_status": booking.booking_status,
                "payment_status": booking.payment_status,
                "base_amount": float(booking.base_amount),
                "final_amount": float(booking.final_amount),
                "amount_paid": float(booking.amount_paid),
                "amount_due": float(booking.amount_due),
                "travel_start_date": booking.travel_start_date.isoformat() if booking.travel_start_date else None,
                "travel_end_date": booking.travel_end_date.isoformat() if booking.travel_end_date else None,
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "confirmed_at": booking.confirmed_at.isoformat() if booking.confirmed_at else None
            }
            for booking in bookings
        ]

        return JsonResponse({
            "bookings": bookings_list,
            "total_count": len(bookings_list)
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_booking(request):
    """
    Update booking status, payment details, or other fields.

    Request Body:
    {
        "transaction_id": 15,
        "booking_status": "confirmed",  // Optional
        "payment_status": "paid",  // Optional
        "amount_paid": 68500.00,  // Optional
        "amount_due": 0.00,  // Optional
        "booking_notes": "Updated notes",  // Optional
        "cancellation_reason": "Customer request",  // Optional (only if cancelling)
        "travel_start_date": "2025-12-05",  // Optional
        "travel_end_date": "2025-12-10"  // Optional
    }

    Response:
    {
        "message": "Booking updated successfully",
        "transaction_id": 15
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        if 'transaction_id' not in data:
            return JsonResponse({"error": "Missing required field: transaction_id"}, status=400)

        with transaction.atomic():
            try:
                booking = Transaction.objects.get(id=data['transaction_id'])
            except Transaction.DoesNotExist:
                return JsonResponse({"error": f"Booking with id {data['transaction_id']} not found"}, status=404)

            # Update booking status
            if 'booking_status' in data:
                booking.booking_status = data['booking_status']

                # Set confirmed_at timestamp
                if data['booking_status'] == 'confirmed' and not booking.confirmed_at:
                    booking.confirmed_at = timezone.now()

                # Set cancelled_at timestamp
                if data['booking_status'] == 'cancelled' and not booking.cancelled_at:
                    booking.cancelled_at = timezone.now()

            # Update payment status
            if 'payment_status' in data:
                booking.payment_status = data['payment_status']

            # Update payment amounts
            if 'amount_paid' in data:
                booking.amount_paid = Decimal(str(data['amount_paid']))

            if 'amount_due' in data:
                booking.amount_due = Decimal(str(data['amount_due']))

            # Update notes
            if 'booking_notes' in data:
                booking.booking_notes = data['booking_notes']

            if 'cancellation_reason' in data:
                booking.cancellation_reason = data['cancellation_reason']

            # Update travel dates
            if 'travel_start_date' in data:
                booking.travel_start_date = data['travel_start_date']

            if 'travel_end_date' in data:
                booking.travel_end_date = data['travel_end_date']

            booking.save()

            return JsonResponse({
                "message": "Booking updated successfully",
                "transaction_id": booking.id,
                "booking_id": booking.id
            }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

