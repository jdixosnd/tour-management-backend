from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your models here.

# Basic admin registration for all models
@admin.register(Touroperator)
class TouroperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'max_users', 'renewal_date', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('renewal_date',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'is_active', 'tour_operator_id')
    search_fields = ('name', 'email', 'mobileno')
    list_filter = ('role', 'is_active', 'tour_operator_id')

#@admin.register(ContactInfo)
#class ContactInfoAdmin(admin.ModelAdmin):
#    list_display = ('name', 'phone', 'email', 'tour_operator', 'description')
#    search_fields = ('name', 'phone', 'email')
#    list_filter = ('tour_operator', 'description')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'tour_operator')
    search_fields = ('name',)
    list_filter = ('type', 'tour_operator')

@admin.register(Inclusion)
class InclusionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'tour_operator')
    search_fields = ('name',)
    list_filter = ('type', 'tour_operator')

@admin.register(Exclusion)
class ExclusionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'tour_operator')
    search_fields = ('name',)
    list_filter = ('type', 'tour_operator')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'tour_operator')
    search_fields = ('name',)
    list_filter = ('type', 'tour_operator')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'country', 'tour_operator')
    search_fields = ('name', 'city', 'state')
    list_filter = ('country', 'tour_operator')

@admin.register(Cardealer)
class CardealerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'location', 'tour_operator')
    search_fields = ('name', 'contact_no')
    list_filter = ('location', 'tour_operator')

@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'capacity', 'tour_operator')
    search_fields = ('name', 'type')
    list_filter = ('tour_operator',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'tour_operator_id', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('tour_operator_id',)

@admin.register(StateCity)
class StateCityAdmin(admin.ModelAdmin):
    list_display = ('state', 'city')
    search_fields = ('state', 'city')

@admin.register(StateCityToDestinationMapping)
class StateCityToDestinationMappingAdmin(admin.ModelAdmin):
    list_display = ('state_city', 'destination')
    search_fields = ('state_city__state', 'state_city__city', 'destination__name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'charges', 'tour_operator', 'created_at')
    search_fields = ('name', 'contact_no')
    list_filter = ('tour_operator',)

@admin.register(SightSeeing)
class SightSeeingAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'charges', 'tour_operator', 'created_at')
    search_fields = ('name', 'contact_no')
    list_filter = ('tour_operator',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'tour_operator', 'ratings', 'phoneno', 'is_active')
    search_fields = ('name', 'phoneno')
    list_filter = ('tour_operator', 'is_active')

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'destination', 'pax_size', 'no_of_days', 'package_amount', 'is_active')
    search_fields = ('name', 'type', 'destination__name')
    list_filter = ('type', 'tour_operator', 'is_active')

@admin.register(DestinationPackageMapping)
class DestinationPackageMappingAdmin(admin.ModelAdmin):
    list_display = ('package_id', 'destination_id', 'day', 'city', 'state', 'tour_operator_id')
    search_fields = ('package_id__name', 'destination_id__name', 'city', 'state')
    list_filter = ('tour_operator_id',)

@admin.register(Itineraryitem)
class ItineraryitemAdmin(admin.ModelAdmin):
    list_display = ('destination', 'item_type', 'description', 'city', 'state')
    search_fields = ('item_type', 'description')
    list_filter = ('tour_operator_id', 'city', 'state')

@admin.register(Packageitineraryitem)
class PackageitineraryitemAdmin(admin.ModelAdmin):
    list_display = ('package', 'itinerary_item', 'day', 'sequence', 'active', 'is_default')
    search_fields = ('package__name', 'itinerary_item__description')
    list_filter = ('active', 'is_default')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'type', 'capacity', 'bedtype', 'rating', 'price_per_night', 'tour_operator')
    search_fields = ('name', 'hotel__name', 'type')
    list_filter = ('tour_operator', 'type', 'bedtype')

@admin.register(PackageHotelMapping)
class PackageHotelMappingAdmin(admin.ModelAdmin):
    list_display = ('package', 'hotel', 'day', 'tour_operator', 'selected_by')
    search_fields = ('package__name', 'hotel__name')
    list_filter = ('tour_operator', 'day')

@admin.register(PackageCarDealerMapping)
class PackageCarDealerMappingAdmin(admin.ModelAdmin):
    list_display = ('package', 'car_dealer', 'day', 'tour_operator', 'selected_by')
    search_fields = ('package__name', 'car_dealer__name')
    list_filter = ('tour_operator', 'day')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email',
                    'tour_operator_id', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('tour_operator_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'package_name', 'package_type',
                    'pax_size', 'proposed_package_amount', 'final_amount', 'created_at')
    search_fields = ('customer__name', 'package_name', 'package_type')
    list_filter = ('tour_operator', 'package_type', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('customer', 'package', 'destination', 'created_by', 'tour_operator')
        }),
        ('Package Details', {
            'fields': ('package_name', 'package_description', 'package_type', 'pax_size', 'contains_travel_fare', 'transport_type', 'no_of_days', 'package_amount')
        }),
        ('Financial Details', {
            'fields': ('proposed_package_amount', 'original_package_amount', 'discount_amount', 'margin_of_profit', 'taxes', 'final_amount')
        }),
        ('Package Features', {
            'fields': ('package_amenities', 'package_inclusions', 'package_exclusions', 'package_policies')
        }),
        ('Other', {
            'fields': ('created_at',)
        })
    )


@admin.register(TransactionDayDetails)
class TransactionDayDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'day', 'hotel_name',
                    'car_dealer_name', 'car_type_name')
    search_fields = ('hotel_name', 'car_dealer_name', 'car_type_name')
    list_filter = ('transaction__tour_operator', 'day')
    ordering = ('transaction', 'day')
    fieldsets = (
        (None, {
            'fields': ('transaction', 'day')
        }),
        ('Hotel Details', {
            'fields': ('hotel', 'hotel_name', 'hotel_description', 'hotel_ratings', 'hotel_phoneno', 'hotel_website', 'hotel_location_city', 'hotel_location_state', 'hotel_location_country')
        }),
        ('Room Details', {
            'fields': (
                'room', 'room_name', 'room_type', 'room_capacity',
                'room_bedtype', 'room_price_per_night',
                'room_amenities', 'room_inclusions', 'room_exclusions', 'room_policies',
            )
        }),

        ('Car Dealer Details', {
            'fields': ('car_dealer', 'car_dealer_name', 'car_dealer_contact', 'car_dealer_location_city', 'car_dealer_location_state', 'car_dealer_location_country', 'car_type', 'car_type_name', 'car_type_capacity')
        }),
        ('Hotel Policies', {
            'fields': ('hotel_amenities', 'hotel_inclusions', 'hotel_exclusions', 'hotel_policies')
        })
    )


@admin.register(TransactionItineraryDetails)
class TransactionItineraryDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_day', 'activity_type',
                    'activity_name', 'charges')
    search_fields = ('activity_name', 'activity_type')
    list_filter = ('activity_type', 'transaction_day__day')
    ordering = ('transaction_day', 'activity_type')
    fieldsets = (
        (None, {
            'fields': ('transaction_day', 'activity_type', 'activity_name', 'activity_description', 'contact_no', 'charges')
        }),
        ('Location Details', {
            'fields': ('location_city', 'location_state', 'location_name', 'location_address', 'location_country')
        })
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'customer__email', 'status')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = 'Customer Name'

@admin.register(LeadPackage)
class LeadPackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'name', 'destination', 'pax_size', 'package_amount', 'created_at')
    list_filter = ('type', 'pax_size', 'contains_travel_fare')
    search_fields = ('name', 'description', 'lead__id', 'destination__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def lead_id(self, obj):
        return obj.lead.id
    lead_id.short_description = 'Lead ID'

@admin.register(LeadDestinationMapping)
class LeadDestinationMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_package', 'destination', 'day', 'city', 'state')
    list_filter = ('day', 'city', 'state')
    search_fields = ('lead_package__name', 'destination__name', 'city', 'state')
    ordering = ('day', 'city', 'state')
    
    def lead_package_name(self, obj):
        return obj.lead_package.name
    lead_package_name.short_description = 'Lead Package Name'

@admin.register(LeadItineraryItem)
class LeadItineraryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_package', 'itinerary_item', 'day', 'sequence', 'created_at')
    list_filter = ('day', 'sequence')
    search_fields = ('lead_package__name', 'itinerary_item__description', 'day')
    ordering = ('day', 'sequence', 'created_at')
    readonly_fields = ('created_at',)
    
    def lead_package_name(self, obj):
        return obj.lead_package.name
    lead_package_name.short_description = 'Lead Package Name'

@admin.register(LeadHotelMapping)
class LeadHotelMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_package', 'hotel', 'day', 'selected_by', 'created_at')
    list_filter = ('day', 'selected_by')
    search_fields = ('lead_package__name', 'hotel__name', 'selected_by__name', 'day')
    ordering = ('day', 'created_at')
    readonly_fields = ('created_at',)
    
    def lead_package_name(self, obj):
        return obj.lead_package.name
    lead_package_name.short_description = 'Lead Package Name'

@admin.register(LeadCarDealerMapping)
class LeadCarDealerMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_package', 'car_dealer', 'day', 'selected_by', 'created_at')
    list_filter = ('day', 'selected_by')
    search_fields = ('lead_package__name', 'car_dealer__name', 'selected_by__name', 'day')
    ordering = ('day', 'created_at')
    readonly_fields = ('created_at',)
    
    def lead_package_name(self, obj):
        return obj.lead_package.name
    lead_package_name.short_description = 'Lead Package Name'

@admin.register(ImageMetadata)
class ImageMetadataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'tour_operator', 
        'module', 
        'record_id', 
        'image_preview',  # Display image preview
        'upload_date', 
        'description', 
        'order'
    )
    list_filter = ('module', 'tour_operator')
    search_fields = ('record_id', 'description', 'tour_operator__name')
    ordering = ('-upload_date',)
    readonly_fields = ('upload_date',)

    def get_queryset(self, request):
        # Customize queryset for additional filtering or ordering if needed
        queryset = super().get_queryset(request)
        return queryset.select_related('tour_operator')

    def image_preview(self, obj):
        # Display image preview in list_display
        if obj.image_path:
            return format_html(f'<img src="{obj.image_path.url}" width="100" height="100" />')
        return "No Image"
    image_preview.short_description = 'Image Preview'

    def save_model(self, request, obj, form, change):
        # Ensure the order field is automatically se    t based on the latest image if order not specified
        if not obj.order:
            last_order = ImageMetadata.objects.filter(
                tour_operator=obj.tour_operator, module=obj.module, record_id=obj.record_id
            ).order_by('-order').first()
            obj.order = last_order.order + 1 if last_order else 1
        super().save_model(request, obj, form, change)

class TourOperatorQuotaAdmin(admin.ModelAdmin):
    list_display = (
        'tour_operator',
        'max_images_destination',
        'max_images_package',
        'max_images_hotel',
        'max_images_room',
        'max_images_car_dealer',
        'max_images_event',
        'max_images_sightseeing',
    )
    list_filter = ('tour_operator',)
    search_fields = ('tour_operator__name',)

    fieldsets = (
        (None, {
            'fields': ('tour_operator',),
            'description': 'Select the tour operator to set quota limits.'
        }),
        ('Image Upload Quotas', {
            'fields': (
                'max_images_destination',
                'max_images_package',
                'max_images_hotel',
                'max_images_room',
                'max_images_car_dealer',
                'max_images_event',
                'max_images_sightseeing',
            ),
            'description': 'Specify the maximum number of images allowed per module for this tour operator.'
        }),
    )

admin.site.register(TourOperatorQuota, TourOperatorQuotaAdmin)