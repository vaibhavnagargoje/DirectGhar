from django.shortcuts import render
# We wrap this import in try/except so your app doesn't crash 
# if you haven't finished the 'listings' models yet.
try:
    from apps.listings.models import Property
except ImportError:
    Property = None

def home(request):
    """
    Renders the Home Page.
    Fetches the 6 most recent active properties to display in the grid.
    """
    recent_properties = []
    
    # Only try to fetch data if the model exists and migrations are applied
    if Property:
        # Get active listings, order by newest, take top 6
        recent_properties = Property.objects.filter(is_active=True).order_by('-created_at')[:6]

    context = {
        'recent_properties': recent_properties,
    }

    return render(request, 'core/index.html', context)

def listings(request):
    return render(request, 'listings/listings.html')