from django import forms
from .models import Property, Amenity

class PropertyForm(forms.ModelForm):
    """Form for creating/editing property listings."""
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'bhk_type', 
            'furnishing_status', 'preferred_tenants',
            'rent_amount', 'deposit_amount', 'maintenance_cost', 'is_negotiable',
            'address', 'locality', 'city', 'state', 'pincode',
            'amenities', 'available_from'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': 'e.g. Spacious 2BHK near Metro Station'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describe your property, nearby landmarks, rules, etc.'
            }),
            'property_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent bg-white'
            }),
            'bhk_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent bg-white'
            }),
            'furnishing_status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent bg-white'
            }),
            'preferred_tenants': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent bg-white'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': '₹ 25000'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': '₹ 100000'
            }),
            'maintenance_cost': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': '₹ 0 (if included)'
            }),
            'is_negotiable': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-brand-orange border-gray-300 rounded focus:ring-brand-orange'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': 'Full address (Building name, Street)'
            }),
            'locality': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': 'e.g. Koramangala, Whitefield'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': 'e.g. Bangalore'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': 'e.g. Karnataka'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'placeholder': '560001'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-transparent',
                'type': 'date'
            }),
        }



class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class PropertyImageForm(forms.Form):
    """Form for uploading property images."""
    images = forms.ImageField(
        widget=MultipleFileInput(attrs={
            'class': 'hidden',
            'multiple': True,
            'accept': 'image/*'
        }),
        required=False
    )
