from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

USER_ROLES = (
    ("manager","Manager"),
    ("user","User"),
)

BED_TYPE = (
    ('single','Single'),
    ('twin','Twin'),
    ('double','Double'),
    ('queen','Queen'),
    ('king','King'),
    ('bunk','Bunk'),
    ('rollaway','Rollaway'),
    ('trundle','Trundle'),
    ('daybed','Daybed'),
    )
ROOM_TYPE = (
    ('studio','Studio'),
    ('standard','Standard'),
    ('delux','Delux'),
    ('suite','Suite'),
    ('superior','Superior'),
    ('superior','Superior'),
    ('family','Family'),
    ('executive','Executive'),
    ('villa','Villa'),
)
TYPE_SERVICE = (
    ('hotel','Hotel'),
    ('room','Room'),
    ('event','Event'),
    ('cardealer','CarDealer'),
)
PACKAGE_TYPES= (
    ('family','Family'),
    ('couple','Couple'),
    ('honeymoon','Honeymoon'),
    ('group','Group'),
)
class Touroperator(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    max_users = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    renewal_date =  models.DateTimeField(null=True,blank=True)
    account_life_months = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    def get_name(self):
        return self.name

    class Meta:
        db_table = 'TourOperator'

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey(Touroperator, blank=True, null=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, blank=True, null=True,default='user',choices = USER_ROLES)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    mobileno = models.CharField(max_length=12, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        return self.name
    def get_name(self):
        return self.name
    
    class Meta:
        db_table = 'User'

class ContactInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    alt_phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255)
    description = models.TextField( blank=True, null=True, choices=TYPE_SERVICE)
    def __str__(self):
        return self.name+"("+self.name+"("+self.phone+")"
    def get_name(self):
        return self.name
    
    class Meta:
        db_table = 'ContactInfo'

class Amenity(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True, choices=TYPE_SERVICE)
    type_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField( blank=True, null=True)

class Inclusion(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True, choices=TYPE_SERVICE)
    type_id = models.BigIntegerField(blank=True, null=True)
    description =  models.TextField( blank=True, null=True)

class Exclusion(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True, choices=TYPE_SERVICE)
    type_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField( blank=True, null=True)

class Policy(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True, choices=TYPE_SERVICE)
    type_id = models.BigIntegerField(blank=True, null=True)
    description =  models.TextField( blank=True, null=True)

class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='created_by', blank=True, null=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    pin_code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    address = models.TextField(max_length=1024,blank=True, null=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name+"("+self.city+", "+self.state+", "+self.country+")"
    def get_name(self):
        return self.name
    
    class Meta:
        db_table = 'Location'
        #unique_together = (('tour_operator', 'name','city', 'country'),)

class Cardealer(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CarDealer'

class CarType(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    car_dealer = models.ForeignKey(Cardealer, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)

class Destination(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by =  models.ForeignKey( User, blank=True, null=True, on_delete=models.CASCADE)
    #location_id = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Destination'
 
class StateCity(models.Model):
    id = models.BigAutoField(primary_key=True)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    def __str__(self):
        return self.city+"("+self.state+")"

class StateCityToDestinationMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    state_city = models.ForeignKey( StateCity, on_delete=models.CASCADE)
    destination =models.ForeignKey( Destination, on_delete=models.CASCADE)
    
class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)#EXACT LOCATION WHERE EVENT OCCURS
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Event'

class SightSeeing(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)#EXACT LOCATION WHERE EVENT OCCURS
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SightSeeing'

class Hotel(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator , blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    ratings = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    website = models.CharField(max_length=45, blank=True, null=True)
    phoneno = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'Hotel'

class Package(models.Model):
    id = models.BigAutoField(primary_key=True)
    destination = models.ForeignKey(Destination, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator , blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100,blank=True, null=True,choices=PACKAGE_TYPES)
    created_at = models.DateTimeField(auto_now=True)
    pax_size = models.IntegerField(blank=True, null=True)
    contains_travel_fare = models.IntegerField(blank=True, null=True)
    transport_type = models.CharField(max_length=45, blank=True, null=True)
    no_of_days = models.IntegerField(blank=True, null=True)
    package_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    notes= models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'Package'

class DestinationPackageMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    package_id = models.ForeignKey( Package, blank=True, null=True, on_delete=models.CASCADE)
    destination_id = models.ForeignKey( Destination, blank=True, null=True, on_delete=models.CASCADE)
    day = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'DestinationPackageMapping'

class Itineraryitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey(Touroperator , blank=True, null=True, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination,  blank=True, null=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    item_type = models.CharField(max_length=50, blank=True, null=True)
    item_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ItineraryItem'

class Packageitineraryitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    package = models.ForeignKey(Package, blank=True, null=True, on_delete=models.CASCADE)
    itinerary_item = models.ForeignKey(Itineraryitem, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    active = models.IntegerField(blank=True, null=True)
    is_default = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'packageItineraryItem'

class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator , blank=True, null=True, on_delete=models.CASCADE)
    created_by= models.ForeignKey(User,blank=True,null=True, on_delete=models.CASCADE)
    type = models.CharField(choices=ROOM_TYPE,max_length=100, blank=True, null=True,default='standard')
    # ADD CAPACITY
    # ADD BED TYPE
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    bedtype = models.CharField(choices=BED_TYPE,max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_night = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'Room'



class PackageHotelMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    day = models.IntegerField()
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PackageHotelMapping'
        unique_together = ('package', 'hotel', 'tour_operator')


class PackageCarDealerMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    car_dealer = models.ForeignKey(Cardealer, on_delete=models.CASCADE)
    day = models.IntegerField()

    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PackageCarDealerMapping'
        unique_together = ('package', 'car_dealer', 'tour_operator')



class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=45, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Customer'



class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    package = models.ForeignKey(Package, on_delete=models.PROTECT)  # Reference to original package
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)  # Reference to original destination
    created_by = models.ForeignKey(User,on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)

    # Snapshot of the offered package details
    package_name = models.CharField(max_length=255)
    package_description = models.TextField(blank=True, null=True)
    package_type = models.CharField(max_length=100)
    pax_size = models.IntegerField(blank=True, null=True)
    contains_travel_fare = models.BooleanField(default=False)
    transport_type = models.CharField(max_length=45, blank=True, null=True)
    no_of_days = models.IntegerField(blank=True, null=True)
    package_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Financial details
    proposed_package_amount = models.DecimalField(max_digits=15, decimal_places=2)
    original_package_amount = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    margin_of_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    taxes = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    final_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Snapshot of package-level amenities, inclusions, exclusions, and policies
    package_amenities = models.JSONField(blank=True, null=True)
    package_inclusions = models.JSONField(blank=True, null=True)
    package_exclusions = models.JSONField(blank=True, null=True)
    package_policies = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Transaction'


class TransactionDayDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, related_name="day_details", on_delete=models.PROTECT)
    day = models.IntegerField()

    # Snapshot of hotel details
    hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.PROTECT)  # Reference to original hotel
    hotel_name = models.CharField(max_length=255, blank=True, null=True)
    hotel_description = models.TextField(blank=True, null=True)
    hotel_ratings = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    hotel_phoneno = models.CharField(max_length=15, blank=True, null=True)
    hotel_website = models.URLField(blank=True, null=True)
    hotel_location_id =  models.ForeignKey(Location, blank=True, null=True, on_delete=models.PROTECT)
    hotel_location_name = models.CharField(max_length=255, blank=True, null=True)
    hotel_location_address = models.CharField(max_length=255, blank=True, null=True)
    hotel_location_city = models.CharField(max_length=255, blank=True, null=True)
    hotel_location_state = models.CharField(max_length=255, blank=True, null=True)
    hotel_location_country = models.CharField(max_length=255, blank=True, null=True)

    # Snapshot of room details
    room = models.ForeignKey(Room, blank=True, null=True, on_delete=models.PROTECT)  # Reference to original hotel
    room_name = models.CharField(max_length=100, blank=True, null=True)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    room_capacity = models.IntegerField(blank=True, null=True)
    room_bedtype = models.CharField(max_length=100, blank=True, null=True)
    room_price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    room_amenities = models.JSONField(blank=True, null=True)
    room_inclusions = models.JSONField(blank=True, null=True)
    room_exclusions = models.JSONField(blank=True, null=True)
    room_policies = models.JSONField(blank=True, null=True)
    
    # Snapshot of car dealer details
    car_dealer = models.ForeignKey(Cardealer, blank=True, null=True, on_delete=models.PROTECT)  # Reference to original car dealer
    car_dealer_name = models.CharField(max_length=255, blank=True, null=True)
    car_dealer_contact = models.CharField(max_length=15, blank=True, null=True)
    car_dealer_location_city = models.CharField(max_length=255, blank=True, null=True)
    car_dealer_location_state = models.CharField(max_length=255, blank=True, null=True)
    car_dealer_location_country = models.CharField(max_length=255, blank=True, null=True)
    car_type = models.ForeignKey(CarType, blank=True, null=True, on_delete=models.PROTECT)  # Reference to original car type
    car_type_name = models.CharField(max_length=255, blank=True, null=True)
    car_type_capacity = models.IntegerField(blank=True, null=True)

    # Snapshot of hotel-level amenities, inclusions, exclusions, and policies
    hotel_amenities = models.JSONField(blank=True, null=True)
    hotel_inclusions = models.JSONField(blank=True, null=True)
    hotel_exclusions = models.JSONField(blank=True, null=True)
    hotel_policies = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'TransactionDayDetails'
        unique_together = ('transaction', 'day')  # Ensure one entry per day for a transaction


class TransactionItineraryDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction_day = models.ForeignKey(TransactionDayDetails, related_name="itinerary_details", on_delete=models.PROTECT)
    
    # Snapshot of itinerary activity details (either event or sightseeing)
    activity_type = models.CharField(max_length=50, choices=[('event', 'Event'), ('sightseeing', 'Sightseeing')])
    activity_name = models.CharField(max_length=255)
    activity_description = models.TextField(blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Snapshot of location details
    location_id =  models.ForeignKey(Location, blank=True, null=True, on_delete=models.PROTECT)
    location_city = models.CharField(max_length=255, blank=True, null=True)
    location_state = models.CharField(max_length=255, blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    location_address = models.TextField(blank=True, null=True)
    location_country = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TransactionItineraryDetails'

