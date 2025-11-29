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
LEAD_STATUS = (('new','New'),
    ('followup','Follow-up'),
    ('active','Active'),
    ('closed','Closed'),
    ('cancelled','Cancelled'),)
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

USER_ROLES = (
    ("manager","Manager"),
    ("user","User"),
)
class Touroperator(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=300)
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
    def get_max_users(self):
        return int(self.max_users)
    def get_account_life_months(self):
        return int(self.account_life_months)

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
    modified_at = models.DateTimeField(blank=True, null=True)
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
    def get_lat_float(self):
        return float(self.lat) if self.lat is not None else None
    def get_lng_float(self):
        return float(self.lng) if self.lng is not None else None

    class Meta:
        db_table = 'Location'
        # Note: Unique constraint is enforced via custom index in migration 0011
        # to avoid MySQL key length limit (using prefix lengths on varchar fields)

class Cardealer(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    image_ids = models.JSONField(default=list, blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'CarDealer'

    def get_images(self):
        """Get all images associated with this car dealer."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this car dealer."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this car dealer."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
    image_ids = models.JSONField(default=list, blank=True, null=True)  # List of image IDs

    def __str__(self):
        return self.name

    @property
    def tour_operator(self):
        return self.tour_operator_id

    class Meta:
        db_table = 'Destination'
        unique_together = [['tour_operator_id', 'name']]

    def get_images(self):
        """Get all images associated with this destination."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this destination."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this destination."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
    location = models.ForeignKey( Location, blank=True, null=True, on_delete=models.CASCADE)  # Link to actual Location object

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
    image_ids = models.JSONField(default=list, blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'Event'

    def get_images(self):
        """Get all images associated with this event."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this event."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this event."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
    image_ids = models.JSONField(default=list, blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'SightSeeing'

    def get_images(self):
        """Get all images associated with this sightseeing."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this sightseeing."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this sightseeing."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
    image_ids = models.JSONField(blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'Hotel'

    def get_images(self):
        """Get all images associated with this hotel."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this hotel."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this hotel."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
    image_ids = models.JSONField(blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'Room'

    def get_images(self):
        """Get all images associated with this room."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this room."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this room."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])


class QuickHotel(models.Model):
    """
    Quick hotel data added directly from package page.
    This is NOT stored in the main Hotel table - it's a lightweight alternative
    for hotels found on-the-fly for specific packages.
    """
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Required fields
    hotel_name = models.CharField(max_length=255)
    room_type = models.CharField(choices=ROOM_TYPE, max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.IntegerField()

    # Optional fields
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'QuickHotel'

    def __str__(self):
        return f"{self.hotel_name} - {self.room_type}"


class Package(models.Model):
    id = models.BigAutoField(primary_key=True)
    destination = models.ForeignKey(Destination, blank=True, null=True, on_delete=models.CASCADE)
    tour_operator = models.ForeignKey(Touroperator , blank=True, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100,blank=True, null=True,choices=PACKAGE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pax_size = models.IntegerField(blank=True, null=True)
    contains_travel_fare = models.IntegerField(blank=True, null=True)
    transport_type = models.CharField(max_length=45, blank=True, null=True)
    no_of_days = models.IntegerField(blank=True, null=True)
    package_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    notes= models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image_ids = models.JSONField(blank=True, null=True)  # List of image IDs
    terms_and_conditions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Package'

    def get_images(self):
        """Get all images associated with this package."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this package."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this package."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

class DestinationPackageMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator_id = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.CASCADE)
    package_id = models.ForeignKey( Package, blank=True, null=True, on_delete=models.CASCADE)
    destination_id = models.ForeignKey( Destination, blank=True, null=True, on_delete=models.CASCADE)
    day = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True)
    description= models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
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
    image_ids = models.JSONField(default=list, blank=True, null=True)  # List of image IDs

    class Meta:
        db_table = 'ItineraryItem'

    def get_images(self):
        """Get all images associated with this itinerary item."""
        from .models import ImageMetadata
        if not self.image_ids:
            return ImageMetadata.objects.none()
        return ImageMetadata.objects.filter(id__in=self.image_ids).order_by('order')

    def add_image_id(self, image_id):
        """Add an image ID to this itinerary item."""
        if self.image_ids is None:
            self.image_ids = []
        if image_id not in self.image_ids:
            self.image_ids.append(image_id)
            self.save(update_fields=['image_ids'])

    def remove_image_id(self, image_id):
        """Remove an image ID from this itinerary item."""
        if self.image_ids and image_id in self.image_ids:
            self.image_ids.remove(image_id)
            self.save(update_fields=['image_ids'])

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
        #unique_together = ('package', 'hotel', 'tour_operator')


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
        #unique_together = ('package', 'car_dealer', 'tour_operator')


class PackageOption(models.Model):
    """
    Represents different pricing/hotel options for a package (e.g., Standard, Deluxe, Premium).
    Each option has its own price and hotel selections for each day.
    """
    id = models.BigAutoField(primary_key=True)
    package = models.ForeignKey(Package, related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., 'Standard', 'Deluxe', 'Premium'
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Price for this option
    description = models.TextField(blank=True, null=True)  # Optional description
    vehicle_type = models.CharField(max_length=255, blank=True, null=True)  # Vehicle/transport type description
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PackageOption'
        ordering = ['id']

    def __str__(self):
        return f"{self.package.name} - {self.name} (₹{self.amount})"


class PackageOptionHotelMapping(models.Model):
    """
    Maps hotels to specific days for each package option.
    This allows different options to have different hotel selections for the same day.
    Can reference either a regular Hotel OR a QuickHotel (one must be set, not both).
    """
    id = models.BigAutoField(primary_key=True)
    package_option = models.ForeignKey(PackageOption, related_name='hotel_mappings', on_delete=models.CASCADE)

    # Either hotel OR quick_hotel must be set (not both)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null=True)
    quick_hotel = models.ForeignKey('QuickHotel', on_delete=models.CASCADE, blank=True, null=True)

    # Room selection (only applicable for regular hotels, not quick hotels)
    selected_room_type = models.ForeignKey('Room', on_delete=models.SET_NULL, blank=True, null=True,
                                          help_text="Selected room type from the hotel")
    room_quantity = models.IntegerField(blank=True, null=True,
                                       help_text="Number of rooms required")

    day = models.IntegerField()  # Day number matching the itinerary
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PackageOptionHotelMapping'
        ordering = ['day', 'id']

    def __str__(self):
        hotel_name = self.hotel.name if self.hotel else (self.quick_hotel.hotel_name if self.quick_hotel else "Unknown")
        return f"{self.package_option.name} - Day {self.day} - {hotel_name}"

    def get_hotel_name(self):
        """Get the hotel name regardless of whether it's a Hotel or QuickHotel"""
        if self.hotel:
            return self.hotel.name
        elif self.quick_hotel:
            return self.quick_hotel.hotel_name
        return None


class PackageOptionCarDealerMapping(models.Model):
    """
    Maps car dealers (transport) to specific days for each package option.
    This allows different options to have different transport selections for the same day.
    """
    id = models.BigAutoField(primary_key=True)
    package_option = models.ForeignKey(PackageOption, related_name='transport_mappings', on_delete=models.CASCADE)
    car_dealer = models.ForeignKey(Cardealer, on_delete=models.CASCADE)
    day = models.IntegerField()  # Day number matching the itinerary
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PackageOptionCarDealerMapping'
        ordering = ['day', 'id']

    def __str__(self):
        return f"{self.package_option.name} - Day {self.day} - {self.car_dealer.name}"


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.ForeignKey( Touroperator, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=45, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=45, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Customer'

######################################################      LEAD RELATED TABLES          #####################################################################
class Lead(models.Model):
    id = models.BigAutoField(primary_key=True),
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, blank=True, null=True,on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=LEAD_STATUS)  # e.g., 'New', 'Follow-up', 'Closed'

    # Travel dates (optional - can be set during lead creation or later)
    travel_start_date = models.DateField(blank=True, null=True)
    travel_end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'Lead'

class LeadPackage(models.Model):
    id = models.BigAutoField(primary_key=True)
    lead = models.ForeignKey(Lead, on_delete=models.PROTECT)
    destination = models.ForeignKey(Destination, blank=True, null=True, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, blank=True, null=True,on_delete=models.PROTECT)

    # Basic package details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100, choices=PACKAGE_TYPES, blank=True, null=True)
    pax_size = models.IntegerField(blank=True, null=True)
    contains_travel_fare = models.BooleanField(default=False)
    transport_type = models.CharField(max_length=45, blank=True, null=True)
    no_of_days = models.IntegerField(blank=True, null=True)
    package_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)

    # Snapshot fields - stored as JSON for complete package data
    package_images = models.JSONField(blank=True, null=True)  # List of image objects
    package_inclusions = models.JSONField(blank=True, null=True)  # List of inclusion objects
    package_exclusions = models.JSONField(blank=True, null=True)  # List of exclusion objects
    package_amenities = models.JSONField(blank=True, null=True)  # List of amenity objects
    package_policies = models.JSONField(blank=True, null=True)  # List of policy objects

    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'LeadPackage'


class LeadDestinationMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    lead_package = models.ForeignKey(LeadPackage, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)

    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)
    day = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True)
    description= models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'LeadDestinationMapping'


class LeadItineraryItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    lead_package = models.ForeignKey(LeadPackage, on_delete=models.PROTECT)
    itinerary_item = models.ForeignKey(Itineraryitem, blank=True, null=True, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, blank=True, null=True,on_delete=models.PROTECT)
    day = models.IntegerField(blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'LeadItineraryItem'


class LeadHotelMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    lead_package = models.ForeignKey(LeadPackage, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    day = models.IntegerField()
    selected_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'LeadHotelMapping'

class LeadCarDealerMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    lead_package = models.ForeignKey(LeadPackage, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, blank=True, null=True, on_delete=models.PROTECT)

    car_dealer = models.ForeignKey(Cardealer, on_delete=models.PROTECT)
    day = models.IntegerField()
    selected_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'LeadCarDealerMapping'


class LeadPackageOption(models.Model):
    """
    Represents different pricing/hotel options for a lead package (snapshot from PackageOption).
    Each option has its own price and hotel selections for each day.
    This is a snapshot - changes to the original PackageOption won't affect this.
    """
    id = models.BigAutoField(primary_key=True)
    lead_package = models.ForeignKey(LeadPackage, related_name='package_options', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)  # e.g., 'Standard', 'Deluxe', 'Premium'
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Price for this option
    description = models.TextField(blank=True, null=True)  # Optional description
    vehicle_type = models.CharField(max_length=255, blank=True, null=True)  # Vehicle/transport type description (snapshot)
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.PROTECT, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LeadPackageOption'
        ordering = ['id']

    def __str__(self):
        return f"{self.lead_package.name} - {self.name} (₹{self.amount})"


class LeadPackageOptionHotelMapping(models.Model):
    """
    Maps hotels to specific days for each lead package option.
    This allows different options to have different hotel selections for the same day.
    This is a snapshot - changes to the original hotel won't affect this.
    Can reference either a regular Hotel OR store QuickHotel data as JSON snapshot.
    """
    id = models.BigAutoField(primary_key=True)
    lead_package_option = models.ForeignKey(LeadPackageOption, related_name='hotel_mappings', on_delete=models.PROTECT)

    # Either hotel OR quick_hotel_data must be set (not both)
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, blank=True, null=True)
    quick_hotel_data = models.JSONField(blank=True, null=True)  # Snapshot of QuickHotel data
    # Format: {"hotel_name": "...", "room_type": "...", "price_per_night": ..., "total_rooms": ..., "address": "...", "phone": "..."}

    # Room selection snapshot (for regular hotels)
    selected_room_type = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True, null=True,
                                          help_text="Selected room type from the hotel (snapshot reference)")
    room_quantity = models.IntegerField(blank=True, null=True,
                                       help_text="Number of rooms required")
    room_snapshot = models.JSONField(blank=True, null=True)  # Snapshot of room data at lead creation time
    # Format: {"id": ..., "name": "...", "type": "...", "capacity": ..., "bedtype": "...", "price_per_night": ..., "description": "...", "images": [...]}

    day = models.IntegerField()  # Day number matching the itinerary
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.PROTECT, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LeadPackageOptionHotelMapping'
        ordering = ['day', 'id']

    def __str__(self):
        hotel_name = self.hotel.name if self.hotel else (self.quick_hotel_data.get('hotel_name') if self.quick_hotel_data else "Unknown")
        return f"{self.lead_package_option.name} - Day {self.day} - {hotel_name}"

    def get_hotel_name(self):
        """Get the hotel name regardless of whether it's a Hotel or QuickHotel"""
        if self.hotel:
            return self.hotel.name
        elif self.quick_hotel_data:
            return self.quick_hotel_data.get('hotel_name')
        return None


class LeadPackageOptionCarDealerMapping(models.Model):
    """
    Maps car dealers (transport) to specific days for each lead package option.
    This allows different options to have different transport selections for the same day.
    This is a snapshot - changes to the original car dealer won't affect this.
    """
    id = models.BigAutoField(primary_key=True)
    lead_package_option = models.ForeignKey(LeadPackageOption, related_name='transport_mappings', on_delete=models.PROTECT)
    car_dealer = models.ForeignKey(Cardealer, on_delete=models.PROTECT)
    day = models.IntegerField()  # Day number matching the itinerary
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.PROTECT, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LeadPackageOptionCarDealerMapping'
        ordering = ['day', 'id']

    def __str__(self):
        return f"{self.lead_package_option.name} - Day {self.day} - {self.car_dealer.name}"


######################################################   TRANSACTION RELATED TABLES      #####################################################################


class Transaction(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    id = models.BigAutoField(primary_key=True)

    # Reference to lead (contains all package options offered to customer)
    lead = models.ForeignKey('Lead', on_delete=models.PROTECT)

    # References for quick access
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    destination = models.ForeignKey(Destination, blank=True, null=True, on_delete=models.PROTECT)

    # Booking details
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # Travel dates
    travel_start_date = models.DateField(blank=True, null=True)
    travel_end_date = models.DateField(blank=True, null=True)

    # Package snapshot (customer's finalized selections from lead options)
    package_name = models.CharField(max_length=255)
    package_description = models.TextField(blank=True, null=True)
    package_type = models.CharField(max_length=100, blank=True, null=True)
    pax_size = models.IntegerField(blank=True, null=True)
    no_of_days = models.IntegerField(blank=True, null=True)

    # Selected package option (if lead had multiple options)
    selected_package_option_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'Deluxe'
    selected_package_option_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Option's base price

    # Snapshot of package-level data (from lead)
    package_inclusions = models.JSONField(blank=True, null=True)
    package_exclusions = models.JSONField(blank=True, null=True)
    package_amenities = models.JSONField(blank=True, null=True)
    package_policies = models.JSONField(blank=True, null=True)
    package_images = models.JSONField(blank=True, null=True)

    # Financial details
    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    taxes = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    final_amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    amount_due = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    # Additional notes
    booking_notes = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Transaction'


class TransactionItineraryItem(models.Model):
    """
    Stores customer's finalized itinerary selections from the lead options.
    Each day has ONE selected hotel and ONE selected transport (chosen from lead's multiple options).
    """
    id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, related_name="itinerary_items", on_delete=models.PROTECT)
    day = models.IntegerField()

    # Day details snapshot (from lead)
    title = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Customer's SELECTED hotel for this day (one from lead's multiple options)
    selected_hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.PROTECT)
    hotel_name = models.CharField(max_length=255, blank=True, null=True)
    hotel_description = models.TextField(blank=True, null=True)
    hotel_images = models.JSONField(blank=True, null=True)

    # QuickHotel data snapshot (if customer selected a quick hotel)
    quick_hotel_data = models.JSONField(blank=True, null=True)
    # Format: {"hotel_name": "...", "room_type": "...", "price_per_night": ..., "total_rooms": ..., "address": "...", "phone": "..."}

    # Room selection snapshot (for regular hotels)
    selected_room_type = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True, null=True,
                                          help_text="Selected room type from the hotel (snapshot reference)")
    room_quantity = models.IntegerField(blank=True, null=True,
                                       help_text="Number of rooms booked")
    room_snapshot = models.JSONField(blank=True, null=True)  # Snapshot of room data at booking time
    # Format: {"id": ..., "name": "...", "type": "...", "capacity": ..., "bedtype": "...", "price_per_night": ..., "description": "...", "images": [...]}

    # Vehicle/transport type description (replaces car dealer references)
    vehicle_type = models.CharField(max_length=255, blank=True, null=True)

    # DEPRECATED: Old car dealer fields - kept for backward compatibility during migration
    selected_car_dealer = models.ForeignKey(Cardealer, blank=True, null=True, on_delete=models.PROTECT)
    car_dealer_name = models.CharField(max_length=255, blank=True, null=True)
    car_type = models.CharField(max_length=255, blank=True, null=True)

    # Activities snapshot (same for all options, so copied from lead)
    activities = models.JSONField(blank=True, null=True)  # List of activity objects

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TransactionItineraryItem'
        unique_together = ('transaction', 'day')


class ImageMetadata(models.Model):
    MODULE_CHOICES = [
        ('destination', 'Destination'),
        ('package', 'Package'),
        ('hotel', 'Hotel'),
        ('room', 'Room'),
        ('car_dealer', 'Car Dealer'),
        ('event', 'Event'),
        ('sightseeing', 'Sightseeing'),
        ('itinerary_item', 'Itinerary Item'),
        ('company_profile', 'Company Profile'),
    ]

    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    record_id = models.BigIntegerField()  # Foreign key to the actual record

    image_path = models.ImageField(upload_to="images/%Y/%m/%d")
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # For displaying images in a specific order

    # Descriptive fields for better identification
    entity_name = models.CharField(max_length=255, blank=True, null=True)  # Name of the hotel, room, etc.
    entity_type = models.CharField(max_length=100, blank=True, null=True)  # Type of room, package, etc.
    parent_entity_name = models.CharField(max_length=255, blank=True, null=True)  # Hotel name for a room, etc.
    parent_entity_id = models.BigIntegerField(blank=True, null=True)  # Hotel ID for a room, etc.

    class Meta:
        db_table = 'ImageMetadata'

    def get_entity(self):
        """Get the entity this image belongs to."""
        if self.module == 'hotel':
            from .models import Hotel
            return Hotel.objects.filter(id=self.record_id).first()
        elif self.module == 'room':
            from .models import Room
            return Room.objects.filter(id=self.record_id).first()
        elif self.module == 'package':
            from .models import Package
            return Package.objects.filter(id=self.record_id).first()
        elif self.module == 'destination':
            from .models import Destination
            return Destination.objects.filter(id=self.record_id).first()
        elif self.module == 'car_dealer':
            from .models import Cardealer
            return Cardealer.objects.filter(id=self.record_id).first()
        elif self.module == 'event':
            from .models import Event
            return Event.objects.filter(id=self.record_id).first()
        elif self.module == 'sightseeing':
            from .models import SightSeeing
            return SightSeeing.objects.filter(id=self.record_id).first()
        elif self.module == 'itinerary_item':
            from .models import Itineraryitem
            return Itineraryitem.objects.filter(id=self.record_id).first()
        return None

    def save(self, *args, **kwargs):
        # Try to set entity_name and entity_type based on the entity
        entity = self.get_entity()
        if entity:
            if hasattr(entity, 'name'):
                self.entity_name = entity.name

            # Set entity_type for rooms
            if self.module == 'room' and hasattr(entity, 'type'):
                self.entity_type = entity.type

            # Set parent_entity_name and parent_entity_id for rooms
            if self.module == 'room' and hasattr(entity, 'hotel') and entity.hotel:
                self.parent_entity_name = entity.hotel.name
                self.parent_entity_id = entity.hotel.id

        super().save(*args, **kwargs)

class TourOperatorQuota(models.Model):
    tour_operator = models.OneToOneField(Touroperator, on_delete=models.CASCADE)
    max_images_destination = models.PositiveIntegerField(default=5)
    max_images_package = models.PositiveIntegerField(default=3)
    max_images_hotel = models.PositiveIntegerField(default=10)
    max_images_room = models.PositiveIntegerField(default=10)
    max_images_car_dealer = models.PositiveIntegerField(default=3)
    max_images_event = models.PositiveIntegerField(default=3)
    max_images_sightseeing = models.PositiveIntegerField(default=3)
    max_images_itinerary_item = models.PositiveIntegerField(default=5)
    max_images_company_profile = models.PositiveIntegerField(default=5)

    class Meta:
        db_table = 'tour_management_touroperatorquota'


class CompanyProfile(models.Model):
    """
    Company Profile model - One profile per tour operator.
    Managers can update, all users can view.
    """
    id = models.BigAutoField(primary_key=True)
    tour_operator = models.OneToOneField(Touroperator, on_delete=models.CASCADE, related_name='company_profile')

    # Basic Company Information
    company_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)

    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)

    # Social Media Links (Optional)
    instagram_url = models.URLField(max_length=500, blank=True, null=True)
    facebook_url = models.URLField(max_length=500, blank=True, null=True)
    twitter_url = models.URLField(max_length=500, blank=True, null=True)
    linkedin_url = models.URLField(max_length=500, blank=True, null=True)
    youtube_url = models.URLField(max_length=500, blank=True, null=True)

    # Business Information
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)

    # Images (stored as JSON list of image IDs)
    logo_image_ids = models.JSONField(default=list, blank=True, null=True)  # Company logo
    banner_image_ids = models.JSONField(default=list, blank=True, null=True)  # Banner/cover images

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_profiles')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_profiles')

    def __str__(self):
        return f"{self.company_name} - {self.tour_operator.name}"

    class Meta:
        db_table = 'CompanyProfile'
