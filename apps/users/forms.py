from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import CustomUser

User = get_user_model()

class PhoneAuthForm(forms.Form):
    phone_number = forms.CharField(
        label="Mobile Number",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-sm focus:ring-2 focus:ring-brand-blue focus:border-brand-blue transition',
            'placeholder': 'Enter 10 digit number',
            'type': 'tel',
            'pattern': '[0-9]{10}'
        }),
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit number.")]
    )

class OTPForm(forms.Form):
    # We will handle the 4 distinct inputs in HTML, but validate as one string here
    otp_code = forms.CharField(max_length=6, min_length=4)

class ProfileCompleteForm(forms.ModelForm):
    # This runs ONLY for new users
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input-std', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input-std', 'placeholder': 'Email Address'}))
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email', 'user_type']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-input-std'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply standard classes
        common_class = 'w-full px-4 py-3 border border-gray-300 rounded-sm focus:ring-2 focus:ring-brand-blue focus:border-brand-blue transition'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = common_class


class UserRegisterForm(UserCreationForm):
    # Add email as a required field
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    
    # Phone number helper
    phone_number = forms.CharField(
        required=True, 
        max_length=15, 
        widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'user_type']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes to all fields Loop
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-sm focus:ring-2 focus:ring-brand-blue focus:border-brand-blue transition duration-150 ease-in-out'
            })
            # Remove generic help text to clean UI
            self.fields[field].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Basic cleanup: remove spaces
        if phone:
            phone = phone.replace(" ", "")
        
        # Unique check (Edge case: Duplicate phones)
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already associated with an account.")
            
        # Optional: Add strict E.164 regex check here or rely on Model validation
        return phone


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-sm focus:ring-2 focus:ring-brand-blue focus:border-brand-blue',
        'placeholder': 'Email or Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-sm focus:ring-2 focus:ring-brand-blue focus:border-brand-blue',
        'placeholder': 'Password'
    }))