from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified_owner', 'account_suspended')
    list_filter = ('user_type', 'is_verified_owner', 'account_suspended', 'flagged_by_system')
    search_fields = ('username', 'email', 'phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile', {'fields': ('user_type', 'phone_number', 'profile_picture')}),
        ('Verification', {'fields': ('is_verified_owner', 'verification_document', 'verification_request_date')}),
        ('Broker Detection', {'fields': ('flagged_by_system', 'flagged_reason', 'flagging_date')}),
        ('Status', {'fields': ('account_suspended', 'suspension_reason', 'last_login_activity')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile', {'fields': ('user_type', 'phone_number', 'email')}),
    )
