from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom User model for DirectGhar, extending Django's AbstractUser.
    """
    class UserType(models.TextChoices):
        OWNER = 'owner', _('Property Owner')
        SEEKER = 'seeker', _('Property Seeker')
        ADMIN = 'admin', _('Administrator')

    user_type = models.CharField(
        max_length=10, 
        choices=UserType.choices, 
        default=UserType.SEEKER, 
        help_text=_('Designates whether the user is a property owner or seeker.')
    )

    # Phone number validation: E.164 format
    phone_regex = RegexValidator(
        regex=r'^\+[1-9]\d{1,14}$', 
        message=_("Phone number must be in E.164 format (e.g., +919876543210)."),
        code='invalid_phone_number'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, null=True, blank=True)

    # --- Profile Specific Fields ---
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, help_text=_("User's profile photo."))
    
    # Fields for OWNERS only
    is_verified_owner = models.BooleanField(
        default=False, 
        help_text=_("Indicates if the owner has passed manual verification.")
    )
    verification_document = models.FileField(
        upload_to='verification_docs/', 
        null=True, 
        blank=True, 
        help_text=_("Owner's document for verification.")
    )
    verification_request_date = models.DateTimeField(null=True, blank=True, help_text=_("Date owner requested verification."))
    
    # --- Broker Detection Specific Fields ---
    flagged_by_system = models.BooleanField(default=False, help_text=_("Flagged by system for potential broker activity."))
    flagged_reason = models.TextField(null=True, blank=True, help_text=_("Reason for system flagging."))
    flagging_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when system flagged the user."))
    
    # Cached counts
    active_listings_count = models.PositiveIntegerField(default=0, help_text=_("Number of active properties listed by this owner."))

    # --- Timestamps and Status ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_activity = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp of last successful login."))
    account_suspended = models.BooleanField(default=False, help_text=_("Is the user's account temporarily or permanently suspended?"))
    suspension_reason = models.TextField(null=True, blank=True, help_text=_("Reason for account suspension."))

    # --- Important for extending AbstractUser ---
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'user_type'] 
    
    def __str__(self):
        return self.get_full_name() or self.username

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = self.phone_number.strip()

    def request_owner_verification(self):
        if self.user_type != self.UserType.OWNER:
            raise ValidationError(_("Only owners can request verification."))
        self.is_verified_owner = False
        self.verification_request_date = timezone.now()
        self.save(update_fields=['is_verified_owner', 'verification_request_date'])

    def approve_owner_verification(self):
        if self.user_type != self.UserType.OWNER:
            raise ValidationError(_("Only owners can be verified."))
        self.is_verified_owner = True
        self.verification_document = None 
        self.verification_request_date = None
        self.save(update_fields=['is_verified_owner', 'verification_document', 'verification_request_date'])

    def reject_owner_verification(self):
        if self.user_type != self.UserType.OWNER:
            raise ValidationError(_("Only owners can be rejected."))
        self.is_verified_owner = False
        self.verification_request_date = None
        self.save(update_fields=['is_verified_owner', 'verification_request_date'])

    def flag_user_as_potential_broker(self, reason=""):
        self.flagged_by_system = True
        self.flagged_reason = reason or "No specific reason provided."
        self.flagging_date = timezone.now()
        self.save(update_fields=['flagged_by_system', 'flagged_reason', 'flagging_date'])

    def unflag_user(self):
        self.flagged_by_system = False
        self.flagged_reason = None
        self.flagging_date = None
        self.save(update_fields=['flagged_by_system', 'flagged_reason', 'flagging_date'])
        
    def suspend_account(self, reason=""):
        self.account_suspended = True
        self.suspension_reason = reason or "Account suspended."
        self.save(update_fields=['account_suspended', 'suspension_reason'])

    def unsuspend_account(self):
        self.account_suspended = False
        self.suspension_reason = None
        self.save(update_fields=['account_suspended', 'suspension_reason'])
        
    def record_login_activity(self):
        self.last_login_activity = timezone.now()
        self.save(update_fields=['last_login_activity'])

    def get_profile_display_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username

class OTPRequest(models.Model):
    phone_number = models.CharField(max_length=17)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.otp_code}"
