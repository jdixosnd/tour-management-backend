import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from tour_management.models import Transaction, Lead, LeadPackage, Touroperator, User
from datetime import datetime, timedelta

@csrf_exempt
def get_sales_analytics(request):
    """
    Returns total revenue, outstanding payments, revenue trend, and revenue by package type.
    """
    if request.method == 'GET':
        try:
            tour_operator_id = request.GET.get('tour_operator_id')
            if not tour_operator_id:
                 return JsonResponse({'error': 'Tour Operator ID is required'}, status=400)

            transactions = Transaction.objects.filter(
                tour_operator__uuid=tour_operator_id
            ).exclude(booking_status='cancelled')

            # 1. Total Revenue
            total_revenue = transactions.aggregate(total=Sum('final_amount'))['total'] or 0

            # 2. Outstanding Payments (Amount Due vs Paid)
            payment_stats = transactions.aggregate(
                total_paid=Sum('amount_paid'),
                total_due=Sum('amount_due')
            )

            # 3. Revenue Trend (Monthly)
            last_12_months = datetime.now() - timedelta(days=365)
            monthly_revenue = transactions.filter(created_at__gte=last_12_months).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                revenue=Sum('final_amount')
            ).order_by('month')

            revenue_trend = [
                {
                    'month': entry['month'].strftime('%Y-%m'), 
                    'revenue': entry['revenue']
                } for entry in monthly_revenue
            ]

            # 4. Revenue by Package Type
            revenue_by_type_qs = transactions.values('package_type').annotate(
                revenue=Sum('final_amount')
            ).order_by('-revenue')

            revenue_by_type = [
                {
                    'type': entry['package_type'] or 'Uncategorized',
                    'revenue': entry['revenue']
                } for entry in revenue_by_type_qs
            ]

            return JsonResponse({
                'status': 'success',
                'data': {
                    'total_revenue': total_revenue,
                    'outstanding_payments': {
                        'paid': payment_stats['total_paid'] or 0,
                        'due': payment_stats['total_due'] or 0
                    },
                    'revenue_trend': revenue_trend,
                    'revenue_by_package_type': revenue_by_type
                }
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_booking_analytics(request):
    """
    Returns booking status overview, monthly volume, and upcoming trips.
    """
    if request.method == 'GET':
        try:
            tour_operator_id = request.GET.get('tour_operator_id')
            if not tour_operator_id:
                 return JsonResponse({'error': 'Tour Operator ID is required'}, status=400)

            transactions = Transaction.objects.filter(tour_operator__uuid=tour_operator_id)

            # 1. Booking Status Overview
            status_counts = transactions.values('booking_status').annotate(
                count=Count('id')
            )
            booking_status_distribution = [
                {'status': entry['booking_status'], 'count': entry['count']} 
                for entry in status_counts
            ]

            # 2. Monthly Booking Volume
            last_12_months = datetime.now() - timedelta(days=365)
            monthly_volume = transactions.filter(created_at__gte=last_12_months).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')

            booking_volume = [
                {
                    'month': entry['month'].strftime('%Y-%m'), 
                    'count': entry['count']
                } for entry in monthly_volume
            ]

            # 3. Upcoming Trips (Next 30 Days)
            today = datetime.now().date()
            next_30_days = today + timedelta(days=30)
            upcoming_trips_qs = transactions.filter(
                travel_start_date__range=[today, next_30_days],
                booking_status__in=['confirmed', 'completed']
            ).values(
                'id', 'package_name', 'customer__name', 'travel_start_date', 'travel_end_date'
            ).order_by('travel_start_date')[:10]

            upcoming_trips = list(upcoming_trips_qs)

            # 4. Cancellations Trend
            cancellations_count = transactions.filter(booking_status='cancelled').count()

            return JsonResponse({
                'status': 'success',
                'data': {
                    'booking_status_distribution': booking_status_distribution,
                    'monthly_booking_volume': booking_volume,
                    'upcoming_trips': upcoming_trips,
                    'total_cancellations': cancellations_count
                }
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_lead_analytics(request):
    """
    Returns lead status distribution, conversion rate, and leads by destination.
    """
    if request.method == 'GET':
        try:
            tour_operator_id = request.GET.get('tour_operator_id')
            if not tour_operator_id:
                 return JsonResponse({'error': 'Tour Operator ID is required'}, status=400)

            leads = Lead.objects.filter(tour_operator__uuid=tour_operator_id)

            # 1. Lead Status Distribution
            status_counts = leads.values('status').annotate(
                count=Count('id')
            )
            lead_status_distribution = [
                {'status': entry['status'], 'count': entry['count']} 
                for entry in status_counts
            ]

            # 2. Lead Conversion Rate
            total_leads = leads.count()
            converted_leads = Transaction.objects.filter(
                tour_operator__uuid=tour_operator_id
            ).count()

            conversion_rate = 0
            if total_leads > 0:
                conversion_rate = round((converted_leads / total_leads) * 100, 2)

            # 3. Leads by Destination
            destination_interest = LeadPackage.objects.filter(
                lead__tour_operator__uuid=tour_operator_id,
                destination__isnull=False
            ).values('destination__name').annotate(
                count=Count('lead')
            ).order_by('-count')[:10]

            leads_by_destination = list(destination_interest)

            return JsonResponse({
                'status': 'success',
                'data': {
                    'lead_status_distribution': lead_status_distribution,
                    'conversion_rate': conversion_rate,
                    'leads_by_destination': leads_by_destination
                }
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_product_analytics(request):
    """
    Returns top selling packages and destinations.
    """
    if request.method == 'GET':
        try:
            tour_operator_id = request.GET.get('tour_operator_id')
            if not tour_operator_id:
                 return JsonResponse({'error': 'Tour Operator ID is required'}, status=400)

            transactions = Transaction.objects.filter(
                tour_operator__uuid=tour_operator_id
            ).exclude(booking_status='cancelled')

            # 1. Top Selling Destinations
            top_destinations = transactions.values('destination__name').annotate(
                bookings=Count('id')
            ).order_by('-bookings')[:10]

            # 2. Top Packages
            top_packages = transactions.values('package_name').annotate(
                bookings=Count('id'),
                revenue=Sum('final_amount')
            ).order_by('-bookings')[:10]

            # 3. Average Booking Value
            avg_booking_val = transactions.aggregate(val=Sum('final_amount')/Count('id'))
            average_booking_value = round(avg_booking_val['val'], 2) if avg_booking_val['val'] else 0

            return JsonResponse({
                'status': 'success',
                'data': {
                    'top_destinations': list(top_destinations),
                    'top_packages': list(top_packages),
                    'average_booking_value': average_booking_value
                }
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_user_performance(request):
    """
    Returns user/team performance metrics: Top Sales Agents, Lead Gen, Conversion Rate.
    """
    if request.method == 'GET':
        try:
            tour_operator_id = request.GET.get('tour_operator_id')
            if not tour_operator_id:
                 return JsonResponse({'error': 'Tour Operator ID is required'}, status=400)

            # 1. Top Sales Agents (by Revenue)
            sales_by_agent = Transaction.objects.filter(
                tour_operator__uuid=tour_operator_id
            ).exclude(booking_status='cancelled').values(
                'created_by__username', 'created_by__id'
            ).annotate(
                total_revenue=Sum('final_amount'),
                bookings_count=Count('id')
            ).order_by('-total_revenue')

            # 2. Lead Generation by Staff
            leads_by_agent = Lead.objects.filter(
                tour_operator__uuid=tour_operator_id
            ).values(
                'created_by__username'
            ).annotate(
                leads_generated=Count('id')
            ).order_by('-leads_generated')
            
            # 3. Conversion Rate by User
            agent_metrics = {}
            
            for lead_stat in leads_by_agent:
                agent = lead_stat['created_by__username'] or 'Unknown'
                if agent not in agent_metrics:
                    agent_metrics[agent] = {'leads': 0, 'bookings': 0, 'revenue': 0}
                agent_metrics[agent]['leads'] = lead_stat['leads_generated']

            for sale_stat in sales_by_agent:
                agent = sale_stat['created_by__username'] or 'Unknown'
                if agent not in agent_metrics:
                     agent_metrics[agent] = {'leads': 0, 'bookings': 0, 'revenue': 0}
                agent_metrics[agent]['bookings'] = sale_stat['bookings_count']
                agent_metrics[agent]['revenue'] = sale_stat['total_revenue']

            performance_table = []
            for agent, metrics in agent_metrics.items():
                leads_count = metrics['leads']
                bookings_count = metrics['bookings']
                conversion_rate = 0
                if leads_count > 0:
                    conversion_rate = round((bookings_count / leads_count) * 100, 1)
                elif bookings_count > 0:
                    conversion_rate = 100 

                avg_booking_val = 0
                if bookings_count > 0:
                    avg_booking_val = round(metrics['revenue'] / bookings_count, 2)

                performance_table.append({
                    'agent': agent,
                    'leads_generated': leads_count,
                    'bookings_closed': bookings_count,
                    'total_revenue': metrics['revenue'],
                    'conversion_rate': conversion_rate,
                    'avg_booking_value': avg_booking_val
                })
            
            performance_table.sort(key=lambda x: x['total_revenue'], reverse=True)

            return JsonResponse({
                'status': 'success',
                'data': {
                    'performance_table': performance_table
                }
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
