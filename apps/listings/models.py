import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# --- 1. AMENITY MODEL (For Scalability) ---
# Using M2M allows you to add "EV Charging" later without changing the whole DB.
class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome or Heroicon class name")
    
    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name

# --- 2. PROPERTY MODEL ---
class Property(models.Model):
    # Enums / Choices
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('independent', 'Independent House/Villa'),
        ('gated_community', 'Gated Community Villa'),
        ('pg', 'Paying Guest (PG)'),
        ('studio', 'Studio Apartment'),
    )

    BHK_TYPES = (
        ('1rk', '1 RK'),
        ('1bhk', '1 BHK'),
        ('2bhk', '2 BHK'),
        ('3bhk', '3 BHK'),
        ('4bhk', '4 BHK'),
        ('4plus', '5+ BHK'),
    )

    FURNISHING_TYPES = (
        ('fully', 'Fully Furnished'),
        ('semi', 'Semi Furnished'),
        ('none', 'Unfurnished'),
    )

    TENANT_PREFERENCE = (
        ('all', 'Any'),
        ('family', 'Family Only'),
        ('bachelor', 'Bachelor (Men)'),
        ('spinster', 'Bachelor (Women)'),
        ('company', 'Company Lease'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('rented', 'Rented Out'),
        ('archived', 'Archived (Deleted)'),
        ('flagged', 'Flagged (Broker Suspected)'),
    )

    # --- IDENTIFICATION ---
    # UUID prevents ID guessing (Scraping Protection)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='properties',
        limit_choices_to={'user_type': 'owner'} # Admin UI restriction
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # --- CORE DETAILS ---
    title = models.CharField(max_length=255, help_text="e.g. Spacious 2BHK in Indiranagar near Metro")
    description = models.TextField(help_text="Describe the property details, nearby landmarks, rules, etc.")
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    bhk_type = models.CharField(max_length=10, choices=BHK_TYPES, blank=True, null=True) # Nullable for PGs
    furnishing_status = models.CharField(max_length=10, choices=FURNISHING_TYPES)
    preferred_tenants = models.CharField(max_length=15, choices=TENANT_PREFERENCE, default='all')
    
    # --- FINANCIALS (Decimal is better for money) ---
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(500)])
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    maintenance_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="0 if included in rent")
    is_negotiable = models.BooleanField(default=False)

    # --- LOCATION ---
    address = models.CharField(max_length=255)
    locality = models.CharField(max_length=100, help_text="e.g. Koramangala, Whitefield")
    city = models.CharField(max_length=50) # In future, make this a ForeignKey to a City model
    state = models.CharField(max_length=50, default='Karnataka')
    pincode = models.CharField(max_length=6, validators=[MinValueValidator('100000')]) # India specific length
    
    # Geolocation for Map Radius Search (Edge Case: Owner might not drop pin)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # --- META & AMENITIES ---
    amenities = models.ManyToManyField(Amenity, blank=True)
    available_from = models.DateField(default=timezone.now)
    
    # --- SYSTEM STATUS ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True, help_text="Switch to toggle visibility instantly")
    view_count = models.PositiveIntegerField(default=0)
    
    # Audit Logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # SPEED UP SEARCH QUERIES
            models.Index(fields=['city', 'locality']),
            models.Index(fields=['rent_amount']),
            models.Index(fields=['bhk_type']),
            models.Index(fields=['status']),
        ]
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} ({self.get_bhk_type_display()}) - {self.city}"

    def save(self, *args, **kwargs):
        # 1. Broker Text Filtering (Basic First Line of Defense)
        # In a real app, do this more gracefully, but here is the logic.
        FORBIDDEN_WORDS = ['brokerage', 'commission', 'consultancy fees', 'agent']
        combined_text = (self.description + " " + self.title).lower()
        
        for word in FORBIDDEN_WORDS:
            if word in combined_text:
                self.status = 'flagged' # Auto-flag
                break

        # 2. SEO Slug Generation
        if not self.slug:
            # Generate: title + random-string -> "2bhk-bangalore-x7z9"
            base_slug = slugify(f"{self.bhk_type} {self.property_type} in {self.locality} {self.city}")
            unique_part = str(uuid.uuid4())[:8] # First 8 chars of uuid
            self.slug = f"{base_slug}-{unique_part}"

        super().save(*args, **kwargs)
        
    def clean(self):
        # 3. Data Integrity Validation
        if self.rent_amount and self.deposit_amount:
            if self.deposit_amount > (self.rent_amount * 12): # Edge Case: Absurd deposit
                raise ValidationError("Deposit amount seems suspiciously high (Max 12 months rent).")
        
        if self.bhk_type is None and self.property_type not in ['pg', 'studio']:
             raise ValidationError("BHK Type is mandatory unless it is a PG or Studio.")

# --- 3. IMAGES MODEL ---
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/%Y/%m/')
    is_primary = models.BooleanField(default=False, help_text="This image will be shown on the listing card.")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Edge Case: Ensure only ONE image is primary per property
        if self.is_primary:
            # Unmark all other images for this property
            PropertyImage.objects.filter(property=self.property, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.property.title}"