from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PropertyForm
from .models import Property, PropertyImage


def listings(request):
    properties = Property.objects.filter(status='active', is_active=True).order_by('-created_at')
    return render(request, 'listings/listings.html', {'properties': properties})

def property_detail(request, id):
    property_obj = get_object_or_404(Property, id=id)
    return render(request, 'listings/property_detail.html', {'property': property_obj})

@login_required(login_url='login')
def create_listing(request):
    """View for creating a new property listing."""
    
    # Only owners can post properties
    if request.user.user_type != 'owner':
        messages.error(request, 'Only registered Property Owners can post listings.')
        return render(request, 'core/error.html', {
            'message': 'Only registered Owners can post properties.'
        })

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            # Assign owner automatically - don't let them choose
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            
            # Save ManyToMany data (amenities)
            form.save_m2m()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for i, image in enumerate(images[:10]):  # Max 10 images
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    is_primary=(i == 0)  # First image is primary
                )
            
            messages.success(request, 'Your property has been listed successfully!')
            return redirect('listings')
    else:
        form = PropertyForm()

    return render(request, 'listings/create_listing.html', {'form': form})

