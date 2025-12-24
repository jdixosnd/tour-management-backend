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
                lead = Lead.objects.select_related('customer', 'tour_operator').get(uuid=data['lead_id'])
            except Lead.DoesNotExist:
                return JsonResponse({"error": f"Lead with id {data['lead_id']} not found"}, status=404)

            # Get lead package to access destination
            try:
                lead_package = LeadPackage.objects.select_related('destination').get(lead=lead)
            except LeadPackage.DoesNotExist:
                return JsonResponse({"error": f"Lead package not found for lead {data['lead_id']}"}, status=404)

            # Get created_by user
            try:
                created_by = User.objects.get(uuid=data['created_by'])
            except User.DoesNotExist:
                return JsonResponse({"error": f"User with id {data['created_by']} not found"}, status=404)

            # Get package snapshot from request or lead
            package_snapshot = data.get('package_snapshot', {})

            # Get selected package option (if customer selected from multiple options)
            selected_option_name = data.get('selected_package_option_name')
            selected_option_amount = data.get('selected_package_option_amount')

            # Get travel dates - use provided dates or copy from lead
            travel_start_date = data.get('travel_start_date') or lead.travel_start_date
            travel_end_date = data.get('travel_end_date') or lead.travel_end_date

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

                # Selected package option (if applicable)
                selected_package_option_name=selected_option_name,
                selected_package_option_amount=Decimal(str(selected_option_amount)) if selected_option_amount else None,

                package_inclusions=package_snapshot.get('inclusions', ''),
                package_exclusions=package_snapshot.get('exclusions', ''),
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

                # Booking details - use provided dates or copy from lead
                travel_start_date=travel_start_date,
                travel_end_date=travel_end_date,
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
                quick_hotel_data = None
                selected_room_type = None
                room_quantity = None
                room_snapshot = None

                if item_data.get('selected_hotel_id'):
                    try:
                        selected_hotel = Hotel.objects.get(uuid=item_data['selected_hotel_id'])
                        hotel_name = selected_hotel.name
                        hotel_description = selected_hotel.description or ''

                        # Get room selection if provided
                        if item_data.get('selected_room_type_id'):
                            try:
                                from ..models import Room
                                selected_room_type = Room.objects.get(uuid=item_data['selected_room_type_id'])
                                room_quantity = item_data.get('room_quantity')
                                room_snapshot = item_data.get('room_snapshot')  # Full room details
                            except Room.DoesNotExist:
                                pass
                    except Hotel.DoesNotExist:
                        pass
                elif item_data.get('quick_hotel_data'):
                    # Handle quick hotel data (snapshot - already has room_type and total_rooms)
                    quick_hotel_data = item_data['quick_hotel_data']
                    hotel_name = quick_hotel_data.get('hotel_name', '')

                # Get vehicle type (new field)
                vehicle_type = item_data.get('vehicle_type', '')

                # DEPRECATED: Old car dealer handling - kept for backward compatibility
                selected_car_dealer = None
                car_dealer_name = ''
                car_type = ''

                if item_data.get('selected_car_dealer_id'):
                    try:
                        selected_car_dealer = Cardealer.objects.get(uuid=item_data['selected_car_dealer_id'])
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
                    quick_hotel_data=quick_hotel_data,

                    # Room selection snapshot (for regular hotels)
                    selected_room_type=selected_room_type,
                    room_quantity=room_quantity,
                    room_snapshot=room_snapshot,

                    vehicle_type=vehicle_type,

                    # DEPRECATED: Old car dealer fields
                    selected_car_dealer=selected_car_dealer,
                    car_dealer_name=car_dealer_name,
                    car_type=item_data.get('car_type', ''),

                    activities=item_data.get('activities', [])
                )

            return JsonResponse({
                "message": "Booking created successfully",
                "transaction_id": str(booking.uuid),
                "booking_id": str(booking.uuid)
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
            ).get(uuid=data['transaction_id'])
        except Transaction.DoesNotExist:
            return JsonResponse({"error": f"Booking with id {data['transaction_id']} not found"}, status=404)

        # Get itinerary items
        itinerary_items = TransactionItineraryItem.objects.filter(
            transaction=booking
        ).select_related('selected_hotel', 'selected_car_dealer', 'selected_room_type').order_by('day')

        # Build response
        response_data = {
            "transaction_id": str(booking.uuid),
            "booking_id": str(booking.uuid),
            "lead_id": str(booking.lead.uuid) if booking.lead else None,

            "customer": {
                "id": str(booking.customer.uuid),
                "name": booking.customer.name,
                "email": booking.customer.email,
                "phone": booking.customer.phone
            },

            "tour_operator": {
                "id": str(booking.tour_operator.uuid),
                "name": booking.tour_operator.name
            },

            "destination": {
                "id": str(booking.destination.uuid),
                "name": booking.destination.name
            } if booking.destination else None,

            "package": {
                "name": booking.package_name,
                "description": booking.package_description,
                "type": booking.package_type,
                "pax_size": booking.pax_size,
                "no_of_days": booking.no_of_days,
                "selected_option": {
                    "name": booking.selected_package_option_name,
                    "amount": float(booking.selected_package_option_amount) if booking.selected_package_option_amount else None
                } if booking.selected_package_option_name else None,
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
                        "id": str(item.selected_hotel.uuid) if item.selected_hotel else None,
                        "name": item.hotel_name,
                        "description": item.hotel_description,
                        "images": item.hotel_images,
                        "quick_hotel_data": item.quick_hotel_data,
                        # Room selection details
                        "selected_room_type_id": str(item.selected_room_type.uuid) if item.selected_room_type else None,
                        "room_quantity": item.room_quantity,
                        "room_snapshot": item.room_snapshot
                    },
                    "vehicle_type": item.vehicle_type,
                    # DEPRECATED: Old transport structure - kept for backward compatibility
                    "transport": {
                        "id": str(item.selected_car_dealer.uuid) if item.selected_car_dealer else None,
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
                "id": str(booking.created_by.uuid),
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
            bookings = bookings.filter(tour_operator__uuid=data['tour_operator'])

        if 'customer_id' in data:
            bookings = bookings.filter(customer__uuid=data['customer_id'])

        if 'booking_status' in data:
            bookings = bookings.filter(booking_status=data['booking_status'])

        if 'payment_status' in data:
            bookings = bookings.filter(payment_status=data['payment_status'])

        if 'destination_id' in data:
            bookings = bookings.filter(destination__uuid=data['destination_id'])

        if 'from_date' in data:
            bookings = bookings.filter(travel_start_date__gte=data['from_date'])

        if 'to_date' in data:
            bookings = bookings.filter(travel_start_date__lte=data['to_date'])

        # Order by created_at descending
        bookings = bookings.order_by('-created_at')

        # Build response
        bookings_list = [
            {
                "transaction_id": str(booking.uuid),
                "booking_id": str(booking.uuid),
                "lead_id": str(booking.lead.uuid) if booking.lead else None,
                "customer_id": str(booking.customer.uuid),
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
                booking = Transaction.objects.get(uuid=data['transaction_id'])
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
                "transaction_id": str(booking.uuid),
                "booking_id": str(booking.uuid)
            }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def delete_booking(request):
    """
    Delete a booking (transaction) and all its related records.

    Required fields:
    - transaction_id: ID of the transaction to delete
    - tour_operator_id: ID of the tour operator (for verification)

    This will delete:
    - Transaction record
    - TransactionItineraryItem records
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        required_keys = ["transaction_id", "tour_operator_id"]
        missing_keys = set(required_keys) - data.keys()

        if missing_keys:
            return JsonResponse(
                {"error": ",".join(missing_keys) + " is/are required fields."},
                status=400
            )

        transaction_id = data['transaction_id']
        tour_operator_id = data['tour_operator_id']

        # Get the transaction and verify it belongs to the tour operator
        try:
            booking = Transaction.objects.get(uuid=transaction_id)
        except Transaction.DoesNotExist:
            return JsonResponse(
                {"error": "Booking not found."},
                status=404
            )

        if booking.tour_operator.uuid != tour_operator_id:
            return JsonResponse(
                {"error": "Booking does not belong to the specified tour operator."},
                status=403
            )

        # Use transaction to ensure all deletes happen atomically
        with transaction.atomic():
            # Delete all itinerary items for this booking
            TransactionItineraryItem.objects.filter(transaction=booking).delete()

            # Delete the booking itself
            customer_name = booking.customer.name if booking.customer else "Unknown"
            package_name = booking.package_name
            booking.delete()

        return JsonResponse(
            {
                "success": f"Booking for customer '{customer_name}' (Package: {package_name}) deleted successfully.",
                "deleted_id": transaction_id
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
