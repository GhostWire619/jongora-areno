from functools import wraps
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from .models import BookingHostProfile, SellerProfile, CustomerProfile


#getting if user is a restaurant seller to direct him/her to restaurant profile and if is a shopping member to redirect to shopping
def business_type_required(*allowed_business_types):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                return redirect('login')  # Redirect to login page if not authenticated
            
            # Get the SellerProfile associated with the authenticated user
            try:
                profile = request.user.sellerprofile
            except SellerProfile.DoesNotExist:
                # Handle the case where the SellerProfile does not exist for the user
                return redirect('index')

            # Check if the user's business type is allowed
            if profile.businesstype in allowed_business_types:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('index')  # Redirect to unauthorized page

        return _wrapped_view
    return decorator


# restricting admins from viewing some pages
def restrict_admin(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            # restrict staff and superusers to access the view
            return redirect('unauthorized')
        else:
            # Allow staff and superusers to access the view
            return view_func(request, *args, **kwargs)
    return _wrapped_view

# allow only admins to admin dashboard
def staff_required(view_func):
    from .views import is_staff
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_staff(request.user):
            return HttpResponseRedirect(reverse('adminlog'))  
        return view_func(request, *args, **kwargs)
    return _wrapped_view

#prevent disabled accounts from viewing pages
def disabled_accounts(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            sellerprofile = None
            hostprofile = None
            # Handle disabled seller accounts
            try:
                sellerprofile = get_object_or_404(SellerProfile, user=request.user)
                if sellerprofile.account_action == 'Disabled':
                    return redirect('disabledaccounts')
            except Http404:
                pass

            # Handle disabled host accounts
            try:
                hostprofile = get_object_or_404(BookingHostProfile, user=request.user)
                if hostprofile.account_action == 'Disabled':
                    return redirect('disabledaccounts')
            except Http404:
                pass

        return view_func(request, *args, **kwargs)
        
    return _wrapped_view

#prevent booking host from viewing pages
def prevent_host(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                host = BookingHostProfile.objects.get(user=request.user)
                if host:
                    return redirect('customer_required')
            except Http404:
                pass
            except BookingHostProfile.DoesNotExist:
                host = None
                pass
        return view_func(request, *args, **kwargs)

    return _wrapped_view

#prevent other users from viewing host account pages
def only_host(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                host = BookingHostProfile.objects.get(user=request.user)
                if host:
                    pass
            except BookingHostProfile.DoesNotExist:
                host = None
                return redirect('index')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


# allow only customers to access these functionalities
def only_customers(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        userprofile = None
        if user.is_authenticated:
            try:
                userprofile = CustomerProfile.objects.get(user=user)
                if userprofile:
                    pass
                else:
                    return redirect('customer_required')
            except CustomerProfile.DoesNotExist:
                userprofile = None
                return redirect('customer_required')

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


