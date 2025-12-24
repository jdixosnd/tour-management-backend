from django.conf.urls import url
from tour_management import views
from django.core.cache import caches
from django.core.cache import cache
import time 
import sys
from django.http import HttpResponse
from django.urls import path

from tour_management.views import probe
from tour_management.controllers import (user, location, destination, hotel,
                                          cardealer, package, event, amenity,
                                            inclusion, exclusion, policy, transaction, touroperator,
                                            lead, customer, booking, company_profile, lead_pdf)
from tour_management import images
urlpatterns = [
    url(r'^tour_management/$',
        views.ApplicationNameParser.as_view()),
        path('touroperator/get/',touroperator.get_tour_operators,name='get_tour_operators'),
        path('touroperator/add/',touroperator.add_tour_operator,name='add_tour_operator'),

        path('user/add/', user.add_user, name='add_user'),
        path('user/get/', user.get_users, name='get_users'),
        path('user/validate/',user.validate_user, name='validate_user'),
        path('user/update/',user.update_user,name='update_user'),
        path('location/add/', location.add_location, name='add_location'),
        path('location/get/', location.get_locations, name='get_locations'),
        path('location/update/',location.update_location, name='update_location'),
        path('location/delete/',location.delete_location, name='delete_location'),

        path('destination/add/', destination.add_destination, name='add_destination'),
        path('destination/get/', destination.get_destinations, name='get_destinations'),
        path('destination/update/', destination.update_destination, name='update_destination'),
        path('destination/delete/', destination.delete_destination, name='delete_destination'),

        path('event/add/', event.add_event, name='add_event'),
        path('event/get/', event.get_events, name='get_events'),

        path('hotel/add/', hotel.add_hotel, name='add_hotel'),
        path('hotel/get/', hotel.get_hotels, name='get_hotels'),
        path('hotel/room/add/',hotel.add_rooms,name='add_rooms'),
        path('hotel/room/get/',hotel.get_rooms,name='get_rooms'),
        path('hotel/room_types/get/',hotel.get_room_types,name='get_room_types'),
        path('hotel/update/',hotel.update_hotel,name='update_hotel'),
        path('hotel/delete/',hotel.delete_hotel,name='delete_hotel'),

        path('cardealer/add/', cardealer.add_cardealer, name='add_cardealer'),
        path('cardealer/get/', cardealer.get_cardealer, name='get_cardealer'),
        path('cardealer/update/',cardealer.update_cardealer, name= 'update_cardealer'),
        path('cardealer/delete/',cardealer.delete_cardealer, name= 'delete_cardealer'),
        path('add_car_type_for_cardealer/add/',cardealer.add_car_type_for_cardealer, name = 'add_car_type_for_cardealer'),

        path('amenity/add/', amenity.add_amenity, name='add_amenity'),
        path('amenity/get/', amenity.get_amenities, name='get_amenities'),
        path('inclusion/add/', inclusion.add_inclusion, name='add_inclusion'),
        path('inclusion/get/', inclusion.get_inclusions, name='get_inclusions'),
        path('exclusion/add/', exclusion.add_exclusion, name='add_exclusion'),
        path('exclusion/get/', exclusion.get_exclusions, name='get_exclusions'),
        path('policy/add/', policy.add_policy, name='add_policy'),
        path('policy/get/', policy.get_policies, name='get_policies'),


        path('package/add/', package.add_package, name='add_package'),
        path('packages_from_destination/get/',package.get_packages_from_destination,name='get_packages_from_destination'),
        path('package/get_all/', package.get_all_packages, name='get_all_packages'),
        path('package/get/', package.get_package, name='get_package'),
        path('package/update/', package.update_package, name='update_package'),
        path('package/delete/', package.delete_package, name='delete_package'),
        path('package/duplicate/', package.duplicate_package, name='duplicate_package'),

        path('transaction/add/',transaction.add_transaction, name='add_transaction'),
        path('transaction/get/',transaction.get_transaction, name='get_transaction'),
        path('transaction/update/',transaction.update_transaction, name='update_transaction'),

        path('lead/add/',lead.add_lead,name='add_lead'),
        path('lead/get/',lead.get_lead,name='get_lead'),
        path('lead/get_all/',lead.get_all_leads,name='get_all_leads'),
        path('lead/update/',lead.update_lead,name='update_lead'),
        path('lead/delete/',lead.delete_lead,name='delete_lead'),
        path('lead/generate_pdf/',lead_pdf.generate_lead_pdf_api,name='generate_lead_pdf'),

        # New Booking APIs (working with Lead-based system)
        path('booking/add/', booking.add_booking, name='add_booking'),
        path('booking/get/', booking.get_booking, name='get_booking'),
        path('booking/get_all/', booking.get_all_bookings, name='get_all_bookings'),
        path('booking/update/', booking.update_booking, name='update_booking'),
        path('booking/delete/', booking.delete_booking, name='delete_booking'),

        path('customer/add/', customer.add_customer, name='add_customer'),
        path('customer/get/', customer.get_customers, name='get_customers'),
        path('customer/update/', customer.update_customer, name='update_customer'),
        path('customer/delete/', customer.delete_customer, name='delete_customer'),

        # Company Profile APIs
        path('company_profile/add/', company_profile.add_company_profile, name='add_company_profile'),
        path('company_profile/get/', company_profile.get_company_profile, name='get_company_profile'),
        path('company_profile/update/', company_profile.update_company_profile, name='update_company_profile'),

        path('image/upload/',images.upload_images,name='upload_images'),
        path('image/get/',images.get_images,name='get_images'),
        path('image/delete/',images.delete_image,name='delete_image'),
        path('probe/',probe)
     ]
