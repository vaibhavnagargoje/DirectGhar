from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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