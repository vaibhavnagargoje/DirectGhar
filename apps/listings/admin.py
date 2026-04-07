from django.contrib import admin
from .models import Property, Amenity, PropertyImage, SavedSearch

# Inline allows you to upload photos DIRECTLY inside the Property page
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3  # Show 3 empty upload slots by default
    fields = ['image', 'is_primary']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    # What shows in the list
    list_display = ('title', 'owner', 'city', 'rent_amount', 'status', 'is_active', 'created_at')
    
    # Sidebar Filters
    list_filter = ('status', 'property_type', 'city', 'bhk_type', 'is_active')
    
    # Search Box functionality
    search_fields = ('title', 'locality', 'owner__email', 'owner__phone_number')
    
    # Slug is auto-generated, but showing it as readonly is good
    readonly_fields = ('slug', 'view_count', 'id')
    
    # Add the images section inside
    inlines = [PropertyImageInline]
    
    # Group fields nicely
    fieldsets = (
        ("Core Details", {
            "fields": ('title', 'owner', 'slug', 'description')
        }),
        ("Specifications", {
            "fields": ('property_type', 'bhk_type', 'furnishing_status', 'amenities',
                       'builtup_area', 'bathrooms', 'floor_number', 'total_floors', 'property_age',
                       'has_parking_2w', 'has_parking_4w', 'non_veg_allowed')
        }),
        ("Financials", {
            "fields": ('rent_amount', 'deposit_amount', 'maintenance_cost', 'is_negotiable')
        }),
        ("Location", {
            "fields": ('address', 'locality', 'city', 'state', 'pincode', 'latitude', 'longitude')
        }),
        ("Management", {
            "fields": ('status', 'is_active', 'preferred_tenants', 'available_from')
        }),
    )

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('label', 'user', 'created_at')
    search_fields = ('label', 'user__email')
    readonly_fields = ('created_at', 'query_string')
