
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
# Import Listing model safely
try:
    from apps.listings.models import Property
except ImportError:
    Property = None

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    
    # --- 1. SETUP DATA BUCKETS ---
    stats = {
        'total_listings': 0,
        'active_listings': 0,
        'total_views': 0,
        'messages_received': 0
    }
    recent_properties = []
    
    # --- 2. FETCH REAL DATA (If Owner) ---
    if user.user_type == 'owner' and Property:
        properties = Property.objects.filter(owner=user).order_by('-created_at')
        
        stats['total_listings'] = properties.count()
        stats['active_listings'] = properties.filter(status='active').count()
        stats['total_views'] = sum(p.view_count for p in properties)
        stats['messages_received'] = 12 # Replace with real count from Message model later
        
        recent_properties = properties[:5]

    # --- 3. DUMMY DATA FALLBACK (For UI Design Preview) ---
    # If the user has NO listings yet, show them what it COULD look like
    # (Or remove this block if you want to show a blank "Empty State")
    if stats['total_listings'] == 0:
        use_dummy = True
        stats = {
            'total_listings': 5,
            'active_listings': 3,
            'total_views': 1240,
            'messages_received': 8
        }
        recent_properties = [
            {
                'title': 'Spacious 2BHK in Indiranagar',
                'location': 'Indiranagar, Bangalore',
                'city': 'Bangalore',
                'rent_amount': 25000,
                'status': 'active',
                'view_count': 450,
                'created_at': '2 days ago',
                'dummy_image': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=500&q=60'
            },
            {
                'title': 'Cozy 1BHK Studio',
                'location': 'Koramangala, Bangalore',
                'city': 'Bangalore',
                'rent_amount': 15000,
                'status': 'rented',
                'view_count': 890,
                'created_at': '1 week ago',
                'dummy_image': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=500&q=60'
            }
        ]
    else:
        use_dummy = False

    context = {
        'section': 'dashboard', # For highlighting sidebar
        'stats': stats,
        'recent_properties': recent_properties,
        'use_dummy': use_dummy
    }
    return render(request, 'users/dashboard.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser, OTPRequest
from .forms import PhoneAuthForm, ProfileCompleteForm
from .utils import generate_otp, verify_otp_logic

def auth_entry(request):
    """
    Step 1: The only entry point. Ask for Phone.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PhoneAuthForm(request.POST)
        if form.is_valid():
            # Format phone to +91... (Assuming India context)
            raw_phone = form.cleaned_data['phone_number']
            phone_number = f"+91{raw_phone}"
            
            # Generate & Send OTP
            generate_otp(phone_number)
            
            # Save phone in session to verify next
            request.session['auth_phone'] = phone_number
            return redirect('verify_otp')
    else:
        form = PhoneAuthForm()

    return render(request, 'users/auth_entry.html', {'form': form})

def verify_otp_view(request):
    """
    Step 2: Verify OTP. Check if Old User or New User.
    """
    phone = request.session.get('auth_phone')
    if not phone:
        return redirect('login')

    if request.method == 'POST':
        # Combine the 4 boxes from HTML into one string
        entered_otp = "".join([request.POST.get(f'otp{i}') for i in range(1, 5)])
        
        if verify_otp_logic(phone, entered_otp):
            # --- CRITICAL BRANCHING LOGIC ---
            try:
                # SCENARIO A: OLD USER -> Login Immediately
                user = CustomUser.objects.get(phone_number=phone)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Cleanup & Redirect
                del request.session['auth_phone']
                messages.success(request, "Welcome back!")
                return redirect('dashboard' if user.user_type == 'owner' else 'home')

            except CustomUser.DoesNotExist:
                # SCENARIO B: NEW USER -> Redirect to Profile Completion
                # We do NOT create the user yet. We keep the phone verified in session.
                request.session['is_phone_verified'] = True
                messages.info(request, "Mobile verified! Please finish your profile.")
                return redirect('complete_profile')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'users/verify_otp.html', {'phone': phone})

def complete_profile_view(request):
    """
    Step 3: Only for New Users. Collect Name/Email/Type.
    """
    phone = request.session.get('auth_phone')
    is_verified = request.session.get('is_phone_verified')

    # Security: Don't let people skip OTP
    if not phone or not is_verified:
        return redirect('login')

    if request.method == 'POST':
        form = ProfileCompleteForm(request.POST)
        if form.is_valid():
            # Create the User
            user = form.save(commit=False)
            user.username = phone # Set phone as username
            user.phone_number = phone
            user.set_unusable_password() # No password needed for OTP users
            user.save()

            # Login
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Cleanup
            if 'auth_phone' in request.session: del request.session['auth_phone']
            if 'is_phone_verified' in request.session: del request.session['is_phone_verified']

            messages.success(request, "Account created successfully!")
            return redirect('dashboard' if user.user_type == 'owner' else 'home')
    else:
        form = ProfileCompleteForm()

    return render(request, 'users/complete_profile.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')