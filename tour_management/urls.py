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
                                            inclusion, exclusion, policy, transaction)

urlpatterns = [
    url(r'^tour_management/$',
        views.ApplicationNameParser.as_view()),
        path('user/add/', user.add_user, name='add_user'),
        path('user/get/', user.get_users, name='get_users'),
        path('user/validate/',user.validate_user, name='validate_user'),

        path('location/add/', location.add_location, name='add_location'),
        path('location/get/', location.get_locations, name='get_locations'),
        path('location/update/',location.update_location, name='update_location'),
        path('location/delete/',location.delete_location, name='delete_location'),

        path('destination/add/', destination.add_destination, name='add_destination'),
        path('destination/get/', destination.get_destinations, name='get_destinations'),

        path('event/add/', event.add_event, name='add_event'),
        path('event/get/', event.get_events, name='get_events'),

        path('hotel/add/', hotel.add_hotel, name='add_hotel'),
        path('hotel/get/', hotel.get_hotels, name='get_hotels'),
        path('hotel/room/add/',hotel.add_rooms,name='add_rooms'),
        path('hotel/room/get/',hotel.get_rooms,name='get_rooms'),
        path('hotel/update/',hotel.update_hotel,name='update_hotel'),

        path('cardealer/add/', cardealer.add_cardealer, name='add_cardealer'),
        path('cardealer/get/', cardealer.get_cardealer, name='get_cardealer'),
        path('cardealer/update/',cardealer.update_cardealer, name= 'update_cardealer'),
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
        path('package/get/', package.get_package, name='get_package'),
        path('package/update/', package.update_package, name='update_package'),

        path('transaction/add/',transaction.add_transaction, name='add_transaction'),
        path('transaction/get/',transaction.get_transaction, name='get_transaction'),
        path('transaction/update/',transaction.update_transaction, name='update_transaction'),
        path('probe/',probe)
     ]