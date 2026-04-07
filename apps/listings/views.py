from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from .forms import PropertyForm
from .models import Property, PropertyImage, SavedSearch


def listings(request):
    """Property search/listing page with full filtering + HTMX partial support."""
    qs = Property.objects.filter(is_active=True, status='active')

    # --- Search ---
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(locality__icontains=q) |
            Q(address__icontains=q) |
            Q(city__icontains=q)
        )

    # City
    city = request.GET.get('city', '').strip()
    if city:
        qs = qs.filter(city__iexact=city)

    # Property type (Full House / PG / Flatmates)
    prop_type = request.GET.get('type', '').strip()
    if prop_type == 'pg':
        qs = qs.filter(property_type='pg')
    elif prop_type == 'flatmates':
        qs = qs.filter(property_type='studio')
    elif prop_type == 'full_house':
        qs = qs.exclude(property_type='pg')

    # BHK Type (can be multi: ?bhk=1bhk&bhk=2bhk)
    bhk_list = request.GET.getlist('bhk')
    if bhk_list:
        qs = qs.filter(bhk_type__in=bhk_list)

    # Rent range
    rent_min = request.GET.get('rent_min', '')
    rent_max = request.GET.get('rent_max', '')
    if rent_min:
        qs = qs.filter(rent_amount__gte=rent_min)
    if rent_max:
        qs = qs.filter(rent_amount__lte=rent_max)

    # Furnishing
    furnishing_list = request.GET.getlist('furnishing')
    if furnishing_list:
        qs = qs.filter(furnishing_status__in=furnishing_list)

    # Preferred tenants
    tenant_list = request.GET.getlist('tenant')
    if tenant_list:
        qs = qs.filter(preferred_tenants__in=tenant_list + ['all'])

    # Availability
    availability = request.GET.get('availability', '').strip()
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    if availability == 'immediate':
        qs = qs.filter(available_from__lte=today)
    elif availability == '15days':
        qs = qs.filter(available_from__lte=today + timedelta(days=15))
    elif availability == '30days':
        qs = qs.filter(available_from__lte=today + timedelta(days=30))

    # ──────────────────────────────────────────────────────────────────────────
    #  PREMIUM FILTERS
    # ──────────────────────────────────────────────────────────────────────────

    # Built-up area range
    area_min = request.GET.get('area_min', '').strip()
    area_max = request.GET.get('area_max', '').strip()
    if area_min:
        qs = qs.filter(builtup_area__gte=area_min)
    if area_max:
        qs = qs.filter(builtup_area__lte=area_max)

    # Bathroom count (multi: ?bathrooms=1&bathrooms=2)
    bathroom_list = request.GET.getlist('bathrooms')
    if bathroom_list:
        int_vals = []
        gte3 = False
        for b in bathroom_list:
            try:
                int_vals.append(int(b))
            except ValueError:
                gte3 = True
        filters = Q(bathrooms__in=int_vals) if int_vals else Q()
        if gte3:
            filters |= Q(bathrooms__gte=3)
        qs = qs.filter(filters)

    # Floor selection (multi-select)
    floor_list = request.GET.getlist('floor')
    if floor_list:
        qs = qs.filter(floor_number__in=floor_list)

    # Property age (multi-select: ?age=lt1&age=lt3)
    age_list = request.GET.getlist('age')
    if age_list:
        qs = qs.filter(property_age__in=age_list)

    # Non-veg allowed
    non_veg = request.GET.get('non_veg', '').strip()
    if non_veg == '1':
        qs = qs.filter(non_veg_allowed=True)

    # Parking
    parking_list = request.GET.getlist('parking')
    if '2w' in parking_list:
        qs = qs.filter(has_parking_2w=True)
    if '4w' in parking_list:
        qs = qs.filter(has_parking_4w=True)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest':    '-created_at',
        'rent_asc':  'rent_amount',
        'rent_desc': '-rent_amount',
        'area_asc':  'builtup_area',
        'relevance': '-view_count',
    }
    qs = qs.order_by(sort_map.get(sort, '-created_at'))

    total = qs.count()

    context = {
        'properties': qs,
        'total': total,
        'query': q,
        'city': city,
        'selected_bhk': bhk_list,
        'rent_min': rent_min or 0,
        'rent_max': rent_max or 500000,
        'area_min': area_min or 0,
        'area_max': area_max or 10000,
        'selected_furnishing': furnishing_list,
        'selected_tenant': tenant_list,
        'selected_floors': floor_list,
        'selected_ages': age_list,
        'selected_bathrooms': bathroom_list,
        'selected_parking': parking_list,
        'availability': availability,
        'sort': sort,
        'get_params': request.GET.urlencode(),
        # Model choices
        'bhk_choices': Property.BHK_TYPES,
        'furnishing_choices': Property.FURNISHING_TYPES,
        'tenant_choices': Property.TENANT_PREFERENCE,
        'property_type_choices': Property.PROPERTY_TYPES,
        'floor_choices': Property.FLOOR_CHOICES,
        'age_choices': Property.PROPERTY_AGE_CHOICES,
        'bathrooms_opts': Property.BATHROOM_CHOICES,
        'availability_choices': [
            ('immediate', 'Immediate'),
            ('15days', 'Within 15 Days'),
            ('30days', 'Within 30 Days'),
            ('later', 'After 30 Days'),
        ],
        'saved_searches': (
            SavedSearch.objects.filter(user=request.user).values('id', 'label', 'query_string')
            if request.user.is_authenticated else []
        ),
    }

    # HTMX: return only the results partial (no full page reload)
    if request.headers.get('HX-Request'):
        return render(request, 'listings/partials/results.html', context)

    return render(request, 'listings/listings.html', context)

def property_detail(request, id):
    property_obj = get_object_or_404(Property, id=id)
    return render(request, 'listings/property_detail.html', {'property': property_obj})

# ── Save Search (POST, AJAX/HTMX) ─────────────────────────────────────────────
@login_required(login_url='login')
@require_POST
def save_search(request):
    label        = request.POST.get('label', '').strip()
    query_string = request.POST.get('query_string', '').strip()
    if not label:
        return JsonResponse({'ok': False, 'error': 'Label is required.'}, status=400)

    obj, created = SavedSearch.objects.get_or_create(
        user=request.user,
        query_string=query_string,
        defaults={'label': label},
    )
    if not created:
        obj.label = label
        obj.save(update_fields=['label'])

    return JsonResponse({'ok': True, 'id': obj.pk, 'created': created})


# ── Delete Saved Search ────────────────────────────────────────────────────────
@login_required(login_url='login')
@require_POST
def delete_saved_search(request, pk):
    obj = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    obj.delete()
    return JsonResponse({'ok': True})


# ── Create Listing ─────────────────────────────────────────────────────────────
@login_required(login_url='login')
def create_listing(request):
    """View for creating a new property listing."""

    if request.user.user_type != 'owner':
        messages.error(request, 'Only registered Property Owners can post listings.')
        return render(request, 'core/error.html', {
            'message': 'Only registered Owners can post properties.'
        })

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            form.save_m2m()

            images = request.FILES.getlist('images')
            for i, image in enumerate(images[:10]):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    is_primary=(i == 0)
                )

            messages.success(request, 'Your property has been listed successfully!')
            return redirect('listings')
    else:
        form = PropertyForm()

    return render(request, 'listings/create_listing.html', {'form': form})

