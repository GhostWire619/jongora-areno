from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
import uuid
import random

#django email
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import HttpResponse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, auth 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test
from django.urls import NoReverseMatch

from .decorators import business_type_required, restrict_admin, disabled_accounts, prevent_host, only_host, staff_required, only_customers
# more functions
from .functions import create_notification, notification_data

#shopping and restaurant
from .models import SellerRegistrationForm, SellerProfile, ShopProduct, ShopCategory, Cart, ShopBrand, RestaurantFoodItem, RestaurantCategory, CustomerProfile, ArenoRating, ArenoContact, ArenoMessage, ArenoAbout, ArenoRefundPolicy, ArenoPrivacyPolicy, PendingPayment, ArenoHomeAd, ArenoShoppingAd, ArenoRestaurantAd, Notification, AdminCustomerNotification, AdminSellerNotification, BookingMainPage
#booking models
from .models import BookingHostForm, BookingHostProfile, ArenoBookingAd, BookingEvent, BookingSports, BookingSportsCategory, BookingEventsCategory, BookingAdventure, BookingAdventureCategory, Following, GeneralPost, BookingCarRental, BookingArenoBnbPropertyFeature, BookingArenoBnb, BookingArenoBnbCategory, BookingRequest, BookingQuestion, BookingCarRequest, sendMessagetoUser, BookingFavourite, UserRate
from .models import BookingCarRentalCategory

#beem sms API
import requests
from requests.auth import HTTPBasicAuth
from .keydetails import beem_url, beem_username, beem_password, beem_source_addr, from_email_title, vat

# Create your views here.
#error handling
from .reports import sellerLoginError, orderDetailsError, foodOrderSummaryError, pendingPaymentError, generalErrorReport

#sms and emails
from .sms_emails import sellerForm, logInCode, contactAreno, emailConfirmationPasswordCustomer, emailConfirmationPasswordSeller, resetPasswordSuccess, verifyEmail, updatedPhonenumber,  registerSellerSuccess, activityForm, bookingactivitysuccess, bookingactivityfailure, HostForm, registerHostSuccess, registerHostDecline, arenoBnbRequest, bookingRequestmessage
from .sms_emails import bookingRequestactionmessage, sendmessage_user


def index(request):
    mainads = ArenoHomeAd.objects.all()
    arenodetails = ArenoContact.objects.all().first()
    user = request.user
    customerprofile = None
    sellerprofile = None
    hostprofile = None
    # Fetch notification data
    notification_context = notification_data(user)


    
    if user.is_authenticated:
        try:
            customerprofile = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist:
            pass

        try:
            sellerprofile = SellerProfile.objects.get(user=user)
        except SellerProfile.DoesNotExist:
            pass

        try:
            hostprofile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist: 
            pass

    
    context = {'arenodetails':arenodetails, 'mainads':mainads, **notification_context, 'customerprofile':customerprofile, 
               'sellerprofile':sellerprofile, 'hostprofile':hostprofile}
    return render(request, 'index.html', context)



#seller registration form
def sellerform(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        businessname = request.POST.get('businessname')
        phonenumber = request.POST.get('phonenumber')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        website = request.POST.get('website')
        address = request.POST.get('address')
        location = request.POST.get('location')
        businesstype = request.POST.get('businesstype')
        if_shoppingcategory = request.POST.get('if_shoppingcategory')
        if_restaurantcategory = request.POST.get('if_restaurantcategory')
        is_businessregistered = request.POST.get('is_businessregistered')
        aboutbusiness = request.POST.get('aboutbusiness')

        if (phonenumber.startswith ('0') or not phonenumber[1:].isdigit()) or (mobile.startswith ('0') or not phonenumber[1:].isdigit()):
            messages.warning(request, 'Write your phone numbers correctly, eg: 255***')
            return redirect('registerform')
        else:
            if (SellerRegistrationForm.objects.filter(email=email).exists()) or (User.objects.filter(username=email)):
                messages.info(request, 'Email  already exists!')
                return redirect('registerform')
            else: 
                if (SellerRegistrationForm.objects.filter(businessname=businessname).exists()) or (SellerProfile.objects.filter(businessname=businessname).exists()):
                    messages.error(request, 'Business Name  already exists!')
                    return redirect('registerform')
                else:
                    sellerform_object = SellerRegistrationForm.objects.create(firstname=firstname, lastname=lastname, businessname=businessname,
                                                                        phonenumber=phonenumber, mobile=mobile,
                                                                        email=email, website=website, address=address, location=location,
                                                                        businesstype=businesstype, if_shoppingcategory=if_shoppingcategory,
                                                                        if_restaurantcategory=if_restaurantcategory, is_businessregistered=is_businessregistered,
                                                                        aboutbusiness=aboutbusiness)
                    sellerform_object.save();
                    messages.success(request, 'Form Successfully Submitted for review, You will be notified soon.')

                    #sms and email sending to user
                    sellerForm(firstname, lastname, phonenumber, email)
                   

                    return redirect ('registerform')
        






def signup(request):
    arenodetails = ArenoContact.objects.all().first()

    context = {'arenodetails':arenodetails}
    return render(request, 'signup.html', context)

def login(request):
    user = request.user

    arenodetails = ArenoContact.objects.all().first()
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        

        user= auth.authenticate(username=username, password=password)
        #trying to get if customer is verified or not
        
        if user is not None:
            try:
                #checking if user is seller to redirect user to seller profile
                profile = SellerProfile.objects.get(user=user)
                if profile.businesstype == 'Shopping':
                    auth.login(request, user)
                    return redirect('shopprofile')
                elif profile.businesstype == 'Restaurant':
                    auth.login(request, user)
                    return redirect('restaurantprofile')
                else: 
                    print('This error occured: User Failed to sign in as a seller')
                    #send bug report
                    sellerLoginError()
                    return redirect('index')
                
            except SellerProfile.DoesNotExist:
                profile = None
                pass

            try:
                customerprofile = CustomerProfile.objects.get(user=user)
                if customerprofile.emailverified == 'Verified':
                    auth.login(request, user)
                    return redirect('index')
                else:
                    random_numbers = [str(random.randint(0, 9)) for _ in range(5)]
                    combined_number = ''.join(random_numbers)
                    customerprofile.usertoken = combined_number
                    customerprofile.save()

                    #send email with the verification code
                    useremail = customerprofile.email
                    userfullname = customerprofile.fullname
                    logInCode(userfullname, combined_number, useremail)

                    return redirect('confirmemail', username=user.username)
            except CustomerProfile.DoesNotExist:
                    customerprofile = None
                    pass
            
            try:
                #check if user is a host and redirect user to host profile
                hostprofile = BookingHostProfile.objects.get(user=user)
                if hostprofile is not None:
                    auth.login(request, user)
                    return redirect('hostprofile')
            except BookingHostProfile.DoesNotExist:
                hostprofile = None
                pass

            print('User profile not found. failed to get user detail to verify email')
            #bug report email
            error = 'User profile not found. failed to get user detail to verify email or to log in'
            pagename = 'login view'
            generalErrorReport(error, 364, pagename)
            return redirect('index')
    
        else:
            messages.error(request, 'Wrong Credentials! please try Again')
            return redirect ('login')
        
    context = {'arenodetails':arenodetails}
    return render(request, 'login.html', context)


@login_required(login_url='login')   
def logout(request):
    auth.logout (request);
    return redirect('index')

def general(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    shopproducts = ShopProduct.objects.filter(action='Approved').order_by('?')
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    restitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('?')

    #DONT DISRUPT THIS CODE BASE!!! Understand it first.
    
    #initialize the dictionary elements to None
    following_true = None
    product = None
    food = None
    event = None
    sport = None
    adventure = None
    #posts search query
    # TODO: Handle this query using only product and food and events unique ids
    query = request.GET.get('query')
    if query:
        pass
        # generalposts = GeneralPost.objects.filter(Q(ItemName__icontains=query) | Q(Description__icontains=query) |
        #                                 Q(Location__icontains=query), Q(status='Approved'))
    else:
        #if no query to display the general posts and its internal elements
        generalposts = GeneralPost.objects.filter(status='Approved')

    
    following_true = None 
    # internal elements of the generalpost to append
    general_posts_with_profiles = []
    for generalpost in generalposts:
        #retrieve post seller details
        try:
            seller_profile = SellerProfile.objects.get(user=generalpost.user)
        except SellerProfile.DoesNotExist:
            seller_profile = None
        #retrieve post host details
        try:
            host_profile = BookingHostProfile.objects.get(user=generalpost.user)
        except BookingHostProfile.DoesNotExist:
            host_profile = None
        #check if user is followed or not
        if request.user.is_authenticated:
            try:
                following_true = Following.objects.filter(user=request.user, following_user=generalpost.user)
            except:
                following_true = None
                try:
                    following_true = Following.objects.filter(user=request.user, following_user=generalpost.user)
                except:
                    following_true = None
                    pass
        else:
            following_true = None
        #retrieve post product/food details
        try:
            product = ShopProduct.objects.get(unique_id=generalpost.Post_Id, action='Approved')
        except ShopProduct.DoesNotExist:
            product = None
        try:
            food = RestaurantFoodItem.objects.get(unique_id=generalpost.Post_Id, action='Approved')
        except RestaurantFoodItem.DoesNotExist:
            food = None
        try:
            event = BookingEvent.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingEvent.DoesNotExist:
            event = None
        try:
            sport = BookingSports.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingSports.DoesNotExist:
            sport = None
        try:
            adventure = BookingAdventure.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingAdventure.DoesNotExist:
            adventure = None
        try:
            car_rental = BookingCarRental.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingCarRental.DoesNotExist:
            car_rental = None
        try:
            arenobnb = BookingArenoBnb.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingArenoBnb.DoesNotExist:
            arenobnb = None
        except Exception as e:
            pass
            
        #appending the internal elements retrival
        general_posts_with_profiles.append({
            'generalpost': generalpost,
            'seller_profile': seller_profile,
            'host_profile':host_profile,
            'following_true': following_true,
            'product':product,
            'food':food,
            'event':event,
            'sport':sport,
            'adventure':adventure,
            'car_rental':car_rental,
            'arenobnb':arenobnb
        })

        
        
   
    
    context = {**notification_context, 'arenodetails':arenodetails, 'shopcats':shopcats, 'shopproducts':shopproducts, 
               'restcategorys':restcategorys, 'restitems':restitems, 'generalposts':generalposts, 'general_posts_with_profiles':general_posts_with_profiles, 
                }
    return render(request, 'general.html', context)

def reels(request):
   
    generalposts = GeneralPost.objects.filter(status='Approved')

    general_posts_with_profiles = []
    for generalpost in generalposts:
        try:
            seller = SellerProfile.objects.get(user=generalpost.user)
        except SellerProfile.DoesNotExist:
            seller = None

        #retrieve post host details
        try:
            host = BookingHostProfile.objects.get(user=generalpost.user)
        except BookingHostProfile.DoesNotExist:
            host = None 

        try:
            product = ShopProduct.objects.get(unique_id = generalpost.Post_Id, action = 'Approved')
        except ShopProduct.DoesNotExist:
            product = None

        try:
            food = RestaurantFoodItem.objects.get(unique_id = generalpost.Post_Id, action = 'Approved')
        except RestaurantFoodItem.DoesNotExist:
            food = None
        
        try:
            event = BookingEvent.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingEvent.DoesNotExist:
            event = None

        try:
            sport = BookingSports.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingSports.DoesNotExist:
            sport = None

        try:
            adventure = BookingAdventure.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingAdventure.DoesNotExist:
            adventure = None

        try:
            car_rental = BookingCarRental.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingCarRental.DoesNotExist:
            car_rental = None

        try:
            arenobnb = BookingArenoBnb.objects.get(unique_id=generalpost.Post_Id, status='Approved')
        except BookingArenoBnb.DoesNotExist:
            arenobnb = None

        except Exception as e:
            pass
        
        general_posts_with_profiles.append({
            'generalpost':generalpost,
            'seller':seller,
            'host':host,
            'product':product,
            'food':food,
            'event':event,
            'sport':sport,
            'adventure':adventure,
            'car_rental':car_rental,
            'arenobnb':arenobnb
        })

    context = {'generalposts':generalposts, 'general_posts_with_profiles': general_posts_with_profiles}
    return render(request, 'reels.html', context)


def customersignup(request):
    user = request.user
    
    arenodetails = ArenoContact.objects.all().first()
    if request.method == 'POST':
        username = request.POST.get('email')
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        access = 'Customer'
        emailverified = 'Not Verified'

        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email  already exists!')
            return redirect('customersignup')
        else:
            if phonenumber.startswith ('0') or not phonenumber[1:].isdigit() :
                messages.warning(request, 'Write your phone number correctly, eg: 255***')
            else:
                if password1 != password2:
                    messages.error(request, 'Passwords do not match!')
                    return redirect('customersignup')
                else:
                    # Create User object
                    #create random token to verify user
                    random_numbers = [str(random.randint(0, 9)) for _ in range(5)]
                    combined_number = ''.join(random_numbers)

                    user = User.objects.create_user(username=username, password=password1, email=email,
                                                    first_name=fullname)
                    # create user profile and save the details
                    Profile = CustomerProfile(user=user, fullname=fullname, email=email, phonenumber=phonenumber, access=access, usertoken=combined_number, emailverified=emailverified)
                    Profile.save();

                    #create a welcome notification alert
                    try:
                        notification_user = user
                        title = 'Welcome to ARENO!'
                        notification_type = 'New Register'
                        content = f"Hi! {fullname}, Get ready to dive into a world of shopping and discover the treasures our sellers have in store for you. Enjoy the experience!"
                        #save the notification
                        notification_object = Notification.objects.create(user=notification_user, title=title, content=content, type=notification_type )
                        notification_object.save();
                    except:
                        pass

                    #email sending email with the verification codes
                    useremail = email
                    userfullname = fullname
                    logInCode(userfullname, combined_number, useremail)


                    return redirect('confirmemail', username)

    context = {'arenodetails':arenodetails}
    return render(request, 'customersignup.html', context)

@only_customers
@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')  
def customerprofile(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()

    followings = Following.objects.filter(user=user)

    #obtain following user details
    followings_sellers = []
    for following in followings:
        useremail = User.objects.get(email = following.following_user)
        try:
            followingseller = SellerProfile.objects.get(id=following.following_user_id, user=useremail)
        except SellerProfile.DoesNotExist:
            followingseller = None
            pass
        try:
            followinghost = BookingHostProfile.objects.get(id=following.following_user_id, user=useremail)
        except BookingHostProfile.DoesNotExist:
            followinghost = None
            pass
        followings_sellers.append({
            'followingseller':followingseller,
            'followinghost':followinghost,
            'following':following
            })

    
        
    following_count = followings.count()
    try:
        customerprofile = get_object_or_404(CustomerProfile, user=user)
    except Exception as e:
        print(e)
        generalErrorReport(e, 433, 'views.py')
        return redirect('index')
    

    context = { **notification_context,'arenodetails':arenodetails, 'followings':followings, 'followings_sellers':followings_sellers, 
               'following_count':following_count, 'customerprofile':customerprofile}
    return render(request, 'customerprofile.html', context)

@only_customers
@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def updatecustomerprofile(request):
    user = request.user
    try:
        customerprofile = get_object_or_404(CustomerProfile, user=user)
        if request.method == 'POST':
            profileimage = request.FILES.get('profileimage')
            if profileimage:
                customerprofile.profileimage = profileimage
            customerprofile.fullname = request.POST.get('fullname')
            customerprofile.phonenumber = request.POST.get('phonenumber')
            customerprofile.location = request.POST.get('location')

            if customerprofile.phonenumber.startswith ('0') or not customerprofile.phonenumber[1:].isdigit() :
                messages.warning(request, 'Write your phone number correctly, eg: 255***')
                return redirect('customerprofile')
            else:
                customerprofile.save()
                redirect_url = request.META.get('HTTP_REFERER')
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    return redirect('customerprofile')
    except Exception as e:
        print(e)
        generalErrorReport(e, 433, 'views.py')
        return redirect('index')

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def followuser(request):
    user = request.user
    try:
        if request.method == 'POST':
            followuser = request.POST.get('followuser')
            followuser_id = request.POST.get('followuser_id')

            if Following.objects.filter(user=user, following_user=followuser, following_user_id=followuser_id).exists():
                pass
                return redirect('general')
            else:
                follow_object = Following.objects.create(user=user, following_user=followuser, following_user_id=followuser_id)
                follow_object.save();

                redirect_url = request.META.get('HTTP_REFERER')
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    return redirect('index')
    except:
        e = 'Failed to follow a user'
        generalErrorReport(e, 438, 'views.py')
        pass

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def unfollowuser(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('unfollowuser')
        user_to_unfollow = get_object_or_404(User, username=username)
        following_object = Following.objects.filter(user=user, following_user= user_to_unfollow)
        following_object.delete();

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('index')
   
@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')   
def addtocart(request, pk=None):
    user = request.user
    if request.method == 'POST':
        item_id  = request.POST.get('itemId')
        item_name = 'Shop Product'

        # get product details
        try:
            shopproduct = get_object_or_404(ShopProduct, id=item_id)
        except SellerProfile.DoesNotExist:
            shopproduct=None

        if Cart.objects.filter(user=user, item_id=item_id, item_name=item_name).exists():
            messages.error(request, "Item already Exists in The Cart! Please Choose another item to add.")
        else:
            cart_item = Cart.objects.create(user=user, item_id=item_id, item_name=item_name )
            messages.success(request, "Item added to the cart Successfully!")
            cart_item.save();

            #save the notification
            create_notification('Added to cart!', 'Cart', f"{shopproduct.productname}", f"{shopproduct.productprice}", user)
            

            return redirect(request.META.get('HTTP_REFERER'))
    # Provide a default fallback URL if referring URL is not available
    return redirect(request.META.get('HTTP_REFERER')) 
    
@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')   
def restaddtocart(request, pk=None):
    user = request.user
    if request.method == 'POST':
        item_id  = request.POST.get('itemId')
        item_name = 'Restaurant Item'

        try:
            restproduct = get_object_or_404(RestaurantFoodItem, id=item_id)
        except SellerProfile.DoesNotExist:
            restproduct=None
        
        if Cart.objects.filter(user=user, item_id=item_id, item_name=item_name).exists():
            messages.error(request, "Item already Exists in The Cart! Please Choose another item to add.")
        else:
            cart_item = Cart.objects.create(user=user, item_id=item_id, item_name=item_name)
            cart_item.save();
            messages.success(request, "Item added to the cart Successfully!")

            #save the notification
            create_notification('Added to cart!', 'Cart', f"{restproduct.productname}", f"{restproduct.productprice}", user)

            return redirect(request.META.get('HTTP_REFERER'))
    # Provide a default fallback URL if referring URL is not available
    return redirect(request.META.get('HTTP_REFERER')) 


# filter products
def product_filter_view(request):
    shopproducts = ShopProduct.objects.filter(action='Approved')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    
    category_name = request.GET.get('category')
    if category_name:
        shopproducts = ShopProduct.objects.filter(Q(productcategory__icontains=category_name), Q(action='Approved'))
    else:
        pass
    

    context = {'shopproducts': shopproducts, 'shopcats':shopcats, 'arenodetails':arenodetails, 'category_name':category_name}
    return render(request, 'products.html', context)

def product_brand_view(request):
    shopproducts = ShopProduct.objects.filter(action='Approved')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    
    brandname = request.GET.get('brand')
    if brandname:
        shopproducts = ShopProduct.objects.filter(Q(productbrand__icontains=brandname), Q(action='Approved'))
    else:
        pass

    
    context = {'shopproducts': shopproducts, 'shopcats':shopcats, 'arenodetails':arenodetails, 'brandname':brandname}
    return render(request, 'products.html', context)

#newest to past
def newproduct(request):
    shopproducts = ShopProduct.objects.filter(action='Approved').order_by('-date')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    
    context = {'shopproducts': shopproducts, 'shopcats':shopcats, 'arenodetails':arenodetails}
    return render(request, 'products.html', context)
#past to newest
def pastproduct(request):
    shopproducts = ShopProduct.objects.filter(action='Approved').order_by('date')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    
    context = {'shopproducts': shopproducts, 'shopcats':shopcats, 'arenodetails':arenodetails}
    return render(request, 'products.html', context)
#new stores
def newstores(request):
    shopstores = SellerProfile.objects.filter(businesstype = 'Shopping').order_by('-date')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')

    context = {'shopstores':shopstores, 'arenodetails':arenodetails, 'shopcats':shopcats}
    return render(request, 'stores.html', context)
#location query
def locationstores(request):
    shopproducts = ShopProduct.objects.filter(action='Approved')
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    arenodetails = ArenoContact.objects.all().first()

    locationquery = request.GET.get('locationquery')
    if locationquery:
        shopproducts = ShopProduct.objects.filter(Q(productlocation__icontains=locationquery), Q(action='Approved'))
    else:
        pass

    context = {'shopproducts': shopproducts, 'shopcats':shopcats, 'arenodetails':arenodetails, 'locationquery':locationquery}
    return render(request, 'products.html', context)

# filter fooditems
def food_filter_view(request):
    restitems = RestaurantFoodItem.objects.filter(action='Approved')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    
    category_name = request.GET.get('category')
    if category_name:
        restitems = RestaurantFoodItem.objects.filter(Q(productcategory__icontains=category_name), Q(action='Approved'))
    else:
        pass


    context = {'restitems': restitems, 'restcategorys':restcategorys, 'arenodetails':arenodetails, 'category_name':category_name}
    return render(request, 'foods.html', context)
#newest to past
def newfoods(request):
    restitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('-date')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    
    context = {'restitems': restitems, 'restcategorys':restcategorys, 'arenodetails':arenodetails}
    return render(request, 'foods.html', context)
#past to newest
def pastfoods(request):
    restitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('date')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    
    context = {'restitems': restitems, 'restcategorys':restcategorys, 'arenodetails':arenodetails}
    return render(request, 'foods.html', context)
#new restaurants
def newrestaurants(request):
    restaurants = SellerProfile.objects.filter(businesstype = 'Restaurant').order_by('-date')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = ShopCategory.objects.all().order_by('categoryname')

    context = {'restaurants':restaurants, 'arenodetails':arenodetails, 'restcategorys':restcategorys}
    return render(request, 'restaurantspage.html', context)
#location query
def locationrestaurants(request):
    restitems = RestaurantFoodItem.objects.filter(action='Approved')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')

    locationquery = request.GET.get('locationquery')
    if locationquery:
        restitems = RestaurantFoodItem.objects.filter(Q(productlocation__icontains=locationquery), Q(action='Approved'))
    else:
        pass

    context = {'restitems': restitems, 'restcategorys':restcategorys, 'arenodetails':arenodetails, 'locationquery':locationquery}
    return render(request, 'foods.html', context)

#delete notification
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_notification(request, notification_type):
    try:
        notification =  Notification.objects.filter(user=request.user, type = notification_type)
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')
    if request.method == 'GET':
        notification.delete();

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('index')





# shopping

def shopping(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    
    shoppingads = ArenoShoppingAd.objects.all().order_by('?')
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    newshopproducts = ShopProduct.objects.filter(action='Approved')
    recommendedshopproducts = ShopProduct.objects.filter(action='Approved').order_by('?')
    blackfridayshopproducts = ShopProduct.objects.filter(action='Approved').order_by('?')
    trendingshopproducts = ShopProduct.objects.filter(action='Approved').order_by('?')
    arenodetails = ArenoContact.objects.all().first()
    

    query = request.GET.get('query')
    try:
        sellerprofile = SellerProfile.objects.all()
        shopcats = ShopCategory.objects.all()
        arenodetails = ArenoContact.objects.all().first()
    except SellerProfile.DoesNotExist:
        sellerprofile = None
        shopcats = None
        arenodetails = None
    if query:
        shopproducts = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved') )
        
        return render(request, 'products.html', {'shopproducts': shopproducts, 'query':query, 'sellerprofile':sellerprofile, 'shopcats':shopcats, 'arenodetails':arenodetails})
    else:
        pass


    context = {**notification_context, 'shoppingads':shoppingads, 'shopcats':shopcats, 'newshopproducts':newshopproducts, 
               'recommendedshopproducts':recommendedshopproducts, 'blackfridayshopproducts':blackfridayshopproducts, 
               'trendingshopproducts':trendingshopproducts, 'arenodetails':arenodetails}
    
    
    return render(request, 'shopping.html', context)


def stores(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shoppingads = ArenoShoppingAd.objects.all().order_by('?')
    shopstores = SellerProfile.objects.filter(businesstype = 'Shopping').order_by('?')
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')

    query = request.GET.get('query')
    if query:
        shopstores = SellerProfile.objects.filter(Q(businessname__icontains=query) | Q(location__icontains=query) |
                                                  Q(bio__icontains=query) | Q(if_shoppingcategory__icontains=query)|
                                                  Q(fullname__icontains=query), businesstype = 'Shopping' )
        

    context = {**notification_context, 'shoppingads':shoppingads, 'shopstores':shopstores, 'arenodetails':arenodetails, 'shopcats':shopcats}
    return render(request, 'stores.html', context)


def shop(request, id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    try:
        shopprofile = get_object_or_404(SellerProfile, id=id)
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')
    products = ShopProduct.objects.filter(user=shopprofile.user, action="Approved")
    shopproduct_count = products.count()
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')

    if user.is_authenticated:
        following_true = Following.objects.filter(user=user, following_user=shopprofile.user)
    else:
        following_true = None
    followers = Following.objects.filter(following_user=shopprofile.user)
    followers_count = followers.count()

    rates = UserRate.objects.filter(selleruser = shopprofile.user )

    query = request.GET.get('query')
    if query:
        products = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | 
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved'), Q(user=shopprofile.user) )
    

    context = {**notification_context, 'rates':rates,
               'shopprofile':shopprofile, 'products':products, 'shopproduct_count':shopproduct_count, 'arenodetails':arenodetails, 'shopcats':shopcats, 'following_true':following_true, 'followers_count':followers_count}
    return render(request, 'shop.html', context)

def brands(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shoppingads = ArenoShoppingAd.objects.all().order_by('?')
    brands = ShopBrand.objects.all().order_by('brand_name')  # Retrieve and sort brand names
    arenodetails = ArenoContact.objects.all().first()
    shopcats = ShopCategory.objects.all().order_by('categoryname')

    # Group brand names by their starting letters
    grouped_brands = {}
    for brand in brands:
        # Check if the brand name is not empty
        if brand.brand_name:
            first_letter = brand.brand_name[0].upper()
            if first_letter not in grouped_brands:
                grouped_brands[first_letter] = []
            grouped_brands[first_letter].append(brand.brand_name)

    query = request.GET.get('query')
    if query:
        brands = ShopBrand.objects.filter(Q(brand_name__icontains=query)).order_by('brand_name')

    context = {**notification_context, 'shoppingads':shoppingads, 'grouped_brands': grouped_brands, 'arenodetails':arenodetails, 'brands': brands, 'shopcats':shopcats}
    return render(request, 'brands.html', context)

def productpage(request, pk=None):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    try:
        shopproduct = ShopProduct.objects.get(pk=pk, action='Approved')
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')
    
    productuser = SellerProfile.objects.get(user=shopproduct.user)
    relatedproducts = ShopProduct.objects.filter(productcategory=shopproduct.productcategory, action='Approved') 
    arenodetails = ArenoContact.objects.all().first()
    
        
    context = {**notification_context, 'shopproduct':shopproduct, 'productuser':productuser, 'relatedproducts':relatedproducts, 'arenodetails':arenodetails}
    return render(request, 'productpage.html', context)

def products(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shopcats = ShopCategory.objects.all()
    shopproducts = ShopProduct.objects.filter(action='Approved').order_by('?')
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    try:
        sellerprofile = SellerProfile.objects.all()
    except SellerProfile.DoesNotExist:
        sellerprofile = None
    if query:
        shopproducts = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved') )

    context = {**notification_context, 'shopcats':shopcats, 'shopproducts':shopproducts, 'arenodetails':arenodetails, 'sellerprofile':sellerprofile, 'query':query}
    return render(request, 'products.html', context)

def categories(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shoppingads = ArenoShoppingAd.objects.all().order_by('?')
    shopcats = ShopCategory.objects.all().order_by('categoryname')
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        shopcats = ShopCategory.objects.filter(Q(categoryname__icontains=query))

    context = {**notification_context, 'shoppingads':shoppingads, 'shopcats':shopcats, 'arenodetails':arenodetails}

    return render(request, 'categories.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def cart(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    
    cartproducts = Cart.objects.filter(user=user)

    cart_items = []
    for cartproduct in cartproducts:

        product = None
        food = None

        try:
            if cartproduct.item_name == 'Shop Product':
                product = ShopProduct.objects.get(id = cartproduct.item_id) # products
            elif cartproduct.item_name == 'Restaurant Item':
                food = RestaurantFoodItem.objects.get(id = cartproduct.item_id) # food items
        except (ShopProduct.DoesNotExist, RestaurantFoodItem.DoesNotExist):
            product = food = None
    
        cart_items.append({
            'cartproduct':cartproduct,
            'product':product,
            'food':food
        })
    
   
    context = { **notification_context, 'cartproducts':cartproducts, 'cart_items':cart_items}
    return render(request, 'cart.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def pendingpurchase(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    pendingproducts = PendingPayment.objects.filter(user=user)

    pending_items = []
    for pendingproduct in pendingproducts:
        product = None
        food = None
        try:
            if pendingproduct.item_name == 'Shop Product':
                product = ShopProduct.objects.get(id= pendingproduct.item_id)
            elif pendingproduct.item_name == 'Restaurant Item':
                food = RestaurantFoodItem.objects.get(id= pendingproduct.item_id)
        except (ShopProduct.DoesNotExist, RestaurantFoodItem.DoesNotExist):
            product = food = None
        pending_items.append({
            'pendingproduct':pendingproduct,
            'product':product,
            'food':food
        })
    

    context = {**notification_context, 'pendingproducts':pendingproducts, 'pending_items':pending_items }
    return render(request, 'pendingpurchase.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_cart_item(request, item_id):
    if request.method == "POST":
        try:
            cart_item = get_object_or_404(Cart, id=item_id)
        except:
            messages.error(request, 'Not Available!')
            return redirect('index')
        # Perform deletion
        cart_item.delete()
        return redirect(request.META.get('HTTP_REFERER')) 
    return redirect(request.META.get('HTTP_REFERER')) 
    
@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_pending_item(request, item_id):
    if request.method == "POST":
        try:
            pending_item = get_object_or_404(PendingPayment, id=item_id)
        except:
            messages.error(request, 'Not Available!')
            return redirect('index')
        
        # Perform deletion
        pending_item.delete()
        return redirect(request.META.get('HTTP_REFERER')) 
    return redirect(request.META.get('HTTP_REFERER'))

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def orderdetails(request , item_id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
        
    #getting user profile informations
    userprofile = None
    try:
        userprofile = CustomerProfile.objects.get( user=user)
        if userprofile:
            userprofile = CustomerProfile.objects.get(user=user)
        elif CustomerProfile.DoesNotExist:
            try:
                userprofile = SellerProfile.objects.get(user=user)
            except SellerProfile.DoesNotExist:
                pass
        else:
            e = 'failed to obtain either one among customer profile details and seller details:'
            orderDetailsError(e)
            pass
    except CustomerProfile.DoesNotExist:
        pass
        userprofile = None
    #handle an error if it occurs
    except Exception as e:
        userprofile = None
        pass
        orderDetailsError(e)

    
    arenodetails = ArenoContact.objects.all().first()
    
    if request.method == 'POST':
        item_id  = int(request.POST.get('itemId'))
        quantity = request.POST.get('quantity')
        item_name = 'Shop Product'
        

        try:
            shopproductuser = get_object_or_404(ShopProduct, id=item_id)
        except SellerProfile.DoesNotExist:
            shopproductuser=None

        if PendingPayment.objects.filter(user=user, item_id=item_id, item_name=item_name).exists():
            #updates the quantity whenever user changes the quantity amount
            try:
                pending = PendingPayment.objects.get(user=user, item_id=item_id, item_name=item_name)
                pending.quantity = request.POST.get('quantity')
                pending.save()
            except:
                pass
            return redirect('orderdetails', item_id)
        else:
            pendingpayment = PendingPayment.objects.create(user=user, item_id=item_id, quantity=quantity, item_name=item_name)
            pendingpayment.save();

            #save the notification
            create_notification('Pending Purchase!', 'pending_purchase', f"{shopproductuser.productname}", f"{shopproductuser.productprice}", user)
            
            return redirect('orderdetails', item_id)

    try:
        product = get_object_or_404(PendingPayment, item_id=item_id, item_name='Shop Product')
        shopproduct = ShopProduct.objects.get(id=product.item_id)

    except:
        shopproduct = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {**notification_context, 'userprofile':userprofile, 'arenodetails':arenodetails, 'shopproduct':shopproduct}

    return render(request, 'orderdetails.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def paymentmethods(request , item_id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()

    try:
        pending = get_object_or_404(PendingPayment, user=user, item_id=item_id, item_name = 'Shop Product' )
    except:
        pending = None
        messages.error(request, 'Not Available!')
        return redirect ('index')

    context = {**notification_context, 'arenodetails':arenodetails, 'pending':pending}
    return render(request, 'paymentmethods.html', context)


#restaurants

def restaurants(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restaurantads = ArenoRestaurantAd.objects.all().order_by('?')
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    restitems = RestaurantFoodItem.objects.filter(action='Approved')
    recommendeditems = RestaurantFoodItem.objects.filter(action='Approved').order_by('?')
    blackfridayitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('?')
    trendingitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('?')
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    try:
        sellerprofile = SellerProfile.objects.all()
        restcategorys = RestaurantCategory.objects.all()
        arenodetails = ArenoContact.objects.all().first()
    except SellerProfile.DoesNotExist:
        sellerprofile = None
        restcategorys = None
        arenodetails = None
    if query:
        restitems = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved') )
        
        return render(request, 'foods.html', {'restitems': restitems, 'query':query, 'sellerprofile':sellerprofile, 'restcategorys':restcategorys, 'arenodetails':arenodetails})
    else:
        pass

    context = {**notification_context, 'restaurantads':restaurantads, 'restcategorys':restcategorys, 'restitems':restitems, 'recommendeditems':recommendeditems, 'blackfridayitems':blackfridayitems, 'trendingitems':trendingitems, 'arenodetails':arenodetails}
    return render(request, 'restaurants.html', context)

def restaurantspage(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restaurantads = ArenoRestaurantAd.objects.all().order_by('?')
    restaurants = SellerProfile.objects.filter(businesstype = 'Restaurant').order_by('?')
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')

    query = request.GET.get('query')
    if query:
        restaurants = SellerProfile.objects.filter(Q(businessname__icontains=query) | Q(location__icontains=query) |
                                                  Q(bio__icontains=query) | Q(if_restaurantcategory__icontains=query)|
                                                  Q(fullname__icontains=query), businesstype = 'Restaurant' )

    context = {**notification_context, 'restaurantads':restaurantads, 'restaurants':restaurants, 'arenodetails':arenodetails, 'restcategorys':restcategorys}
    return render(request, 'restaurantspage.html', context)

def restaurantpage(request, id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    
    try:
        restprofile = get_object_or_404(SellerProfile, id=id)
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')
    fooditems = RestaurantFoodItem.objects.filter(user=restprofile.user, action="Approved")
    fooditems_count = fooditems.count()
    arenodetails = ArenoContact.objects.all().first()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')

    if user.is_authenticated:
        following_true = Following.objects.filter(user=user, following_user=restprofile.user)
    else:
        following_true = None
    followers = Following.objects.filter(following_user=restprofile.user)
    followers_count = followers.count()

    rates = UserRate.objects.filter(selleruser = restprofile.user )

    query = request.GET.get('query')
    if query:
        fooditems = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | 
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved'), Q(user=restprofile.user) )

    context = {**notification_context, 'restprofile':restprofile, 'fooditems':fooditems, 'fooditems_count':fooditems_count,  'rates':rates,
               'arenodetails':arenodetails, 'restcategorys':restcategorys, 'following_true':following_true, 'followers_count':followers_count}
    return render(request, 'restaurantpage.html', context)

def foodpage(request, pk=None):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    try:
        fooditem = RestaurantFoodItem.objects.get(pk=pk, action='Approved')
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')
    productuser = SellerProfile.objects.get(user=fooditem.user)
    relatedproducts = RestaurantFoodItem.objects.filter(productcategory=fooditem.productcategory, action='Approved')
    arenodetails = ArenoContact.objects.all().first() 
    
        
    context = {**notification_context, 'fooditem':fooditem, 'productuser':productuser, 'relatedproducts':relatedproducts, 'arenodetails':arenodetails}
    return render(request, 'foodpage.html', context)


def foods(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    restitems = RestaurantFoodItem.objects.filter(action='Approved').order_by('?')
    arenodetails = ArenoContact.objects.all().first() 

    query = request.GET.get('query')
    try:
        sellerprofile = SellerProfile.objects.all()
    except SellerProfile.DoesNotExist:
        sellerprofile = None
    if query:
        restitems = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved') )

    context = {**notification_context, 'restcategorys':restcategorys, 'restitems':restitems, 'arenodetails':arenodetails, 'sellerprofile':sellerprofile}
    return render(request, 'foods.html', context)

def meals(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restaurantads = ArenoRestaurantAd.objects.all().order_by('?')
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    arenodetails = ArenoContact.objects.all().first() 

    query = request.GET.get('query')
    if query:
        restcategorys = RestaurantCategory.objects.filter(Q(categoryname__icontains=query))

    context = {**notification_context, 'restaurantads':restaurantads, 'restcategorys':restcategorys, 'arenodetails':arenodetails}
    return render(request, 'meals.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def foodordersummary(request, item_id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    #getting user profile informations
    userprofile = None
    try:
        userprofile = CustomerProfile.objects.get( user=user)
        if userprofile:
            userprofile = CustomerProfile.objects.get(user=user)
        elif CustomerProfile.DoesNotExist:
            try:
                userprofile = SellerProfile.objects.get(user=user)
            except SellerProfile.DoesNotExist:
                pass
        else:
            e = 'failed to obtain either one among customer profile details and seller details:'
            foodOrderSummaryError(e)
            pass
    #handle an error if it occurs
    except CustomerProfile.DoesNotExist:
        pass
        userprofile = None
    except Exception as e:
        userprofile = None
        foodOrderSummaryError(e)
        pass

    
    arenodetails = ArenoContact.objects.all().first()
    
    if request.method == 'POST':
        item_id  = int(request.POST.get('itemId'))
        quantity = request.POST.get('quantity')
        item_name = 'Restaurant Item'
        

        try:
            shopproductuser = get_object_or_404(RestaurantFoodItem, id=item_id)
        except SellerProfile.DoesNotExist:
            shopproductuser=None

        if PendingPayment.objects.filter(user=user, item_id=item_id, item_name=item_name).exists():
            #updates the quantity whenever user changes the quantity amount
            try:
                pending = PendingPayment.objects.get(user=user, item_id=item_id, item_name=item_name)
                pending.quantity = request.POST.get('quantity')
                pending.save()
            except:
                pass
            return redirect('foodordersummary', item_id)
        else:
            pendingpayment = PendingPayment.objects.create(user=user, item_id=item_id, quantity=quantity, item_name=item_name)
            pendingpayment.save();

             #save the notification
            create_notification('Pending Purchase!', 'pending_purchase_food', f"{shopproductuser.productname}", f"{shopproductuser.productprice}", user)
            

            return redirect( 'foodordersummary', item_id)

    try:
        product = get_object_or_404(PendingPayment, item_id=item_id, item_name='Restaurant Item')
        restproduct = RestaurantFoodItem.objects.get(id=product.item_id)
    except:
        restproduct = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {**notification_context, 'userprofile':userprofile, 'arenodetails':arenodetails, 'restproduct':restproduct}
    return render(request, 'foodordersummary.html', context)

def restaurantpaymentmethods(request , item_id):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    arenodetails = ArenoContact.objects.all().first() 

    try:
        pending = get_object_or_404(PendingPayment, user=user, item_id=item_id, item_name = 'Restaurant Item' )
    except:
        pending = None
        messages.error(request, 'Not Available!')
        return redirect ('index')

    context = {**notification_context, 'arenodetails':arenodetails, 'pending':pending}
    return render(request, 'restaurantpaymentmethods.html', context)


#profile pages
@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Shopping')
def profilepage(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    shopprofile = SellerProfile.objects.get(user=user)
    shopproducts = ShopProduct.objects.filter(user=user, action='Approved')
    shopproduct_count = shopproducts.count()
    shopcategorys = ShopCategory.objects.all().order_by('categoryname')
    arenodetails = ArenoContact.objects.all().first() 
    followers = Following.objects.filter(following_user=shopprofile.user)
    followers_count = followers.count()
    followings = Following.objects.filter(user = shopprofile.user)

    #obtain following user details
    followings_sellers = []
    for following in followings:
        useremail = User.objects.get(email = following.following_user)
        try:
            followingseller = SellerProfile.objects.get(id=following.following_user_id, user=useremail)
        except SellerProfile.DoesNotExist:
            followingseller = None
            pass
        try:
            followinghost = BookingHostProfile.objects.get(id=following.following_user_id, user=useremail)
        except BookingHostProfile.DoesNotExist:
            followinghost = None
            pass
        followings_sellers.append({
            'followingseller': followingseller,
            'followinghost':followinghost,
            'following':following
            })
    
    following_count = followings.count()

    #products search
    query = request.GET.get('query')
    if query:
        shopproducts = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | 
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved'), Q(user=shopprofile.user) )

    context = {**notification_context, 'shopprofile':shopprofile, 'shopproducts':shopproducts, 'shopproduct_count':shopproduct_count, 
               'shopcategorys':shopcategorys, 'arenodetails':arenodetails, 'followers_count':followers_count, 'followings':followings, 'followings_sellers':followings_sellers, 'following_count':following_count}
    return render(request, 'profilepage.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Shopping')
def pendingproducts(request):
    user = request.user
    profile = SellerProfile.objects.get(user = user)
    products = ShopProduct.objects.filter(user = user, action=None)

    query = request.GET.get('query')
    if query:
        products = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(productcategory__icontains=query) |
                                                Q(productprice__icontains=query) , Q(action=None), Q(user=user) )


    context = {'products':products, 'profile':profile}
    return render(request, 'pendingproducts.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Shopping')
def declinedproducts(request):
    user = request.user
    profile = SellerProfile.objects.get(user = user)
    products = ShopProduct.objects.filter(user = user, action='Declined')

    query = request.GET.get('query')
    if query:
        products = ShopProduct.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(productcategory__icontains=query) |
                                                Q(productprice__icontains=query) , Q(action='Declined'), Q(user=user) )


    context = {'products':products, 'profile':profile}
    return render(request, 'declinedproducts.html', context)

@prevent_host
@disabled_accounts
@restrict_admin 
@business_type_required('Shopping')
def editproduct(request, pk):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shopprofile = get_object_or_404(SellerProfile, user=user)
    arenodetails = ArenoContact.objects.all().first() 

    try:
        product = get_object_or_404(ShopProduct, action='Approved', pk=pk)
        productcats = ShopCategory.objects.all()
    except:
        product = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    #save the product details
    if request.method == 'POST':
        product.productname = request.POST.get('name')
        product.productprice = request.POST.get('price')
        product.productsize = request.POST.get('size','')
        product.productweight = request.POST.get('weight','')
        product.productavailability = request.POST.get('availability','')
        product.productcolor = request.POST.get('color','')
        product.productlocation = request.POST.get('location')
        product.productcategory = request.POST.get('category','')
        product.productstatus = request.POST.get('status','')
        brand = request.POST.get('brand','')
        product.productbrand = brand if brand else None


        product.save()
        return redirect ('shopprofile')
    
    context = {**notification_context, 'shopprofile':shopprofile, 'arenodetails':arenodetails,
                'product':product, 'productcats':productcats}

    return render(request, 'editproduct.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Shopping')
def deleteshopproduct(request, pk=None):
    try:
        shopproduct = ShopProduct.objects.get(id=pk)
    except:
        shopproduct = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    cartitems = Cart.objects.filter(item_id=pk, item_name='Shop Product')
    pendingitems = PendingPayment.objects.filter(item_id=pk, item_name='Shop Product')
    try:
        generalpost = GeneralPost.objects.get(Post_Id=shopproduct.unique_id)
    except:
        generalpost = None
    
    if request.method == 'POST':
        shopproduct.delete();
        if cartitems:
            cartitems.delete()
        if pendingitems:
            pendingitems.delete()
        if generalpost:
            generalpost.delete()

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('shopprofile')

@prevent_host
@disabled_accounts
@restrict_admin 
@business_type_required('Shopping')
def shopsettings(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    shopprofile = get_object_or_404(SellerProfile, user=user)
    arenodetails = ArenoContact.objects.all().first() 
    activeitems = ShopProduct.objects.filter(user=user, action='Approved')
    activecounter = activeitems.count()
    pendingitems = ShopProduct.objects.filter(user=user, action=None)
    pendingcounter = pendingitems.count()
    declineditems = ShopProduct.objects.filter(user=user, action='Declined')
    declinedcounter = declineditems.count()

    rates = UserRate.objects.filter(selleruser = user )

    if request.method == 'POST':

        profileimage = request.FILES.get('profileimage')
        if profileimage:
            shopprofile.profileimage = profileimage

        if_shoppingcategory = request.POST.get('activity')
        if if_shoppingcategory:
            shopprofile.if_shoppingcategory = if_shoppingcategory

        shopprofile.location = request.POST.get('location', '')
        shopprofile.phonenumber = request.POST.get('phonenumber', '')
        shopprofile.mobile = request.POST.get('mobile', '')
        shopprofile.email = request.POST.get('email', '')
        shopprofile.working_start_hour = request.POST.get('working_start_hour', '')
        shopprofile.working_end_hour = request.POST.get('working_end_hour', '')

        working_start_day = request.POST.get('working_start_day', '')
        if working_start_day:
            shopprofile.working_start_day = working_start_day

        working_end_day = request.POST.get('working_end_day', '')
        if working_end_day:
            shopprofile.working_end_day = working_end_day

        shopprofile.bio = request.POST.get('bio', '')


        #prevent user to input any contact related items
        forbidden_words = ['facebook', 'instagram', 'whatsapp', 'twitter', 'youtube']

        if (any(char.isdigit() for char in shopprofile.bio) 
            or '@' in shopprofile.bio
            or any(word in shopprofile.bio.lower() for word in forbidden_words)):
            messages.warning(request, 'Please DO NOT include numbers and any other contact-related informations in your biography!')
            return redirect('shopsettings')
        else:
            if shopprofile.phonenumber.startswith ('0') or not shopprofile.phonenumber[1:].isdigit() :
                messages.error(request, 'Write your phone number correctly, eg: 255***')
                return redirect('shopsettings')
            else:
                shopprofile.save();
    
        return redirect ('shopprofile')
    
    context = {**notification_context, 'shopprofile':shopprofile, 'arenodetails':arenodetails,
               'activecounter':activecounter, 'pendingcounter':pendingcounter, 'declinedcounter':declinedcounter, 'rates':rates}

    return render(request, 'shopsettings.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Shopping')
def postproduct(request):
    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        productimage = request.FILES.get('image1')
        productimage2 = request.FILES.get('image2')
        productimage3 = request.FILES.get('image3')
        productimage4 = request.FILES.get('image4')
        productimage5 = request.FILES.get('image5')
        productvideo = request.FILES.get('video')
        productname = request.POST.get('name')
        productprice = request.POST.get('price')
        productsize = request.POST.get('size')
        productweight = request.POST.get('weight')
        productavailability = request.POST.get('availability')
        productcolor = request.POST.get('color')
        productlocation = request.POST.get('location')
        productcategory = request.POST.get('category')
        productstatus = request.POST.get('status')
        brand = request.POST.get('brand','')
        productbrand = brand if brand else None
        productdescription = request.POST.get('description')

        #to prevent user form inputing any contact related info
        forbidden_words = ['facebook', 'instagram', 'whatsapp', 'twitter', 'youtube']

        if productimage == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            if (any(word in productdescription.lower() for word in forbidden_words) 
                or any(char.isdigit() for char in productdescription) 
                or '@' in productdescription):
                messages.warning(request, 'Please DO NOT include any contact-related informations in your item description!')

            else:
                product_object = ShopProduct.objects.create(user=request.user, unique_id=unique_id, productname=productname, productimage=productimage,
                                                        productimage2=productimage2, productimage3=productimage3, productimage4=productimage4, productimage5=productimage5,
                                                        productvideo=productvideo, productprice=productprice, productsize=productsize, productweight=productweight,
                                                        productavailability=productavailability, productcolor=productcolor, productstatus=productstatus,
                                                        productlocation=productlocation, productcategory=productcategory, productbrand=productbrand,
                                                        productdescription=productdescription)
                
                product_object.save();
                # create a general post
                GeneralPost.objects.create(Post_Id=unique_id, Type='ShopProduct') # creates general post instance

                if not ShopBrand.objects.filter(brand_name=productbrand).exists():
                    ShopBrand.objects.create(brand_name=productbrand) # save brand
            messages.success(request, 'Submitted Successfully! Your Item will be reviewed before being displayed on your page and other pages.')
    
        return redirect('shopprofile')
    return redirect(request.META.get('HTTP_REFERER'))

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Restaurant')
def restaurantprofile(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restprofile = get_object_or_404(SellerProfile, user=request.user)
    restproducts = RestaurantFoodItem.objects.filter(user = request.user, action='Approved')
    restproduct_count = restproducts.count()
    restcategorys = RestaurantCategory.objects.all().order_by('categoryname')
    arenodetails = ArenoContact.objects.all().first() 
    followers = Following.objects.filter(following_user=restprofile.user)
    followers_count = followers.count()
    followings = Following.objects.filter(user = restprofile.user)

    #obtain following user details
    followings_sellers = []
    for following in followings:
        useremail = User.objects.get(email = following.following_user)
        try:
            followingseller = SellerProfile.objects.get(id=following.following_user_id, user=useremail)
        except SellerProfile.DoesNotExist:
            followingseller = None
            pass
        try:
            followinghost = BookingHostProfile.objects.get(id=following.following_user_id, user=useremail)
        except BookingHostProfile.DoesNotExist:
            followinghost = None
            pass
        followings_sellers.append({
            'followingseller': followingseller,
            'followinghost':followinghost,
            'following':following
            })
    following_count = followings.count()

    query = request.GET.get('query')
    if query:
        restproducts = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | 
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query) , Q(action='Approved'), Q(user=restprofile.user) )
    

    context = {**notification_context, 'restprofile':restprofile, 'restproducts':restproducts, 'restproduct_count':restproduct_count, 
               'restcategorys':restcategorys, 'arenodetails':arenodetails, 'followers_count':followers_count, 'followings':followings, 'followings_sellers':followings_sellers, 'following_count':following_count }
    return render(request, 'restaurantprofile.html', context)
 
@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Restaurant')
def pendingfooditems(request):
    user = request.user
    restprofile = SellerProfile.objects.get(user = user)
    restproducts = RestaurantFoodItem.objects.filter(user = user, action=None)

    query = request.GET.get('query')
    if query:
        restproducts = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(productcategory__icontains=query) |
                                                Q(productprice__icontains=query) , Q(action=None), Q(user=user) )


    context = {'restproducts':restproducts, 'restprofile':restprofile}
    return render(request, 'pendingfooditems.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Restaurant')
def declinedfooditems(request):
    user = request.user
    restprofile = SellerProfile.objects.get(user = user)
    restproducts = RestaurantFoodItem.objects.filter(user = user, action='Declined')

    query = request.GET.get('query')
    if query:
        restproducts = RestaurantFoodItem.objects.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(productcategory__icontains=query) |
                                                Q(productprice__icontains=query) , Q(action='Declined'), Q(user=user) )


    context = {'restproducts':restproducts, 'restprofile':restprofile}
    return render(request, 'declinedfooditems.html', context)

@prevent_host
@disabled_accounts
@restrict_admin 
@business_type_required('Restaurant')
def editfood(request, pk):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restprofile = get_object_or_404(SellerProfile, user=user)
    arenodetails = ArenoContact.objects.all().first() 

    try:
        food = get_object_or_404(RestaurantFoodItem, action='Approved', pk=pk)
        foodcats = RestaurantCategory.objects.all()
    except:
        food = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    if request.method == 'POST':
        food.productname = request.POST.get('name')
        food.productprice = request.POST.get('price')
        food.productsize = request.POST.get('size','')
        food.productweight = request.POST.get('weight','')
        food.productavailability = request.POST.get('availability','')
        food.productcolor = request.POST.get('color','')
        food.productlocation = request.POST.get('location')
        food.productcategory = request.POST.get('category','')
        food.productstatus = request.POST.get('status','')

        food.save()
        return redirect ('restaurantprofile')
    
    context = {**notification_context, 'restprofile':restprofile, 'arenodetails':arenodetails, 
               'food':food, 'foodcats':foodcats}

    return render(request, 'editfood.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Restaurant')
def deletefooditem(request, pk=None):
    try:
        fooditem = get_object_or_404(RestaurantFoodItem, id=pk)
    except:
        fooditem = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    cartitems = Cart.objects.filter(item_id=pk, item_name='Restaurant Item')
    pendingitems = PendingPayment.objects.filter(item_id=pk, item_name='Restaurant Item')
    try:
        generalpost = GeneralPost.objects.get(Post_Id=fooditem.unique_id)
    except:
        generalpost = None
        pass

    if request.method == 'POST':
        fooditem.delete();
        if cartitems:
            cartitems.delete()
        if pendingitems:
            pendingitems.delete()
        if generalpost:
            generalpost.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('restaurantprofile')

@disabled_accounts
@restrict_admin 
@business_type_required('Restaurant')
def restaurantsettings(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    restprofile = get_object_or_404(SellerProfile, user=user)
    arenodetails = ArenoContact.objects.all().first() 
    activeitems = RestaurantFoodItem.objects.filter(user=user, action='Approved')
    activecounter = activeitems.count()
    pendingitems = RestaurantFoodItem.objects.filter(user=user, action=None)
    pendingcounter = pendingitems.count()
    declineditems = RestaurantFoodItem.objects.filter(user=user, action='Declined')
    declinedcounter = declineditems.count()

    rates = UserRate.objects.filter(selleruser = user )

    if request.method == 'POST':

        profileimage = request.FILES.get('profileimage', '')
        if profileimage:
            restprofile.profileimage = profileimage

        if_restaurantcategory = request.POST.get('activity')
        if if_restaurantcategory:
            restprofile.if_restaurantcategory = if_restaurantcategory

        restprofile.location = request.POST.get('location', '')
        restprofile.phonenumber = request.POST.get('phonenumber', '')
        restprofile.mobile = request.POST.get('mobile', '')
        restprofile.email = request.POST.get('email', '')
        restprofile.working_start_hour = request.POST.get('working_start_hour', '')
        restprofile.working_end_hour = request.POST.get('working_end_hour', '')

        working_start_day = request.POST.get('working_start_day', '')
        if working_start_day:
            restprofile.working_start_day = working_start_day

        working_end_day = request.POST.get('working_end_day', '')
        if working_end_day:
            restprofile.working_end_day = working_end_day

        restprofile.bio = request.POST.get('bio', '')

        #to prevent user to input any contact related info
        forbidden_words = ['facebook', 'instagram', 'whatsapp', 'twitter', 'youtube']

        if (any(char.isdigit() for char in restprofile.bio) 
            or '@' in restprofile.bio
            or any(word in restprofile.bio.lower() for word in forbidden_words)):
            messages.warning(request, 'Please DO NOT include numbers and any other contact-related informations in your biography!')
            return redirect('restaurantsettings')
        else:
            if restprofile.phonenumber.startswith ('0') or not restprofile.phonenumber[1:].isdigit() :
                messages.error(request, 'Write your phone number correctly, eg: 255***')
                return redirect('restaurantsettings')
            else:
                restprofile.save();
    
        return redirect ('restaurantprofile')
    
    context = {**notification_context, 'restprofile':restprofile, 'arenodetails':arenodetails, 'activecounter':activecounter, 
                'pendingcounter':pendingcounter, 'declinedcounter':declinedcounter, 'rates':rates }

    return render(request, 'restaurantsettings.html', context)

@prevent_host
@disabled_accounts
@restrict_admin
@business_type_required('Restaurant')
def postfood(request):
    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        productimage = request.FILES.get('image1')
        productimage2 = request.FILES.get('image2')
        productimage3 = request.FILES.get('image3')
        productimage4 = request.FILES.get('image4')
        productimage5 = request.FILES.get('image5')
        productvideo = request.FILES.get('video')
        productname = request.POST.get('name')
        productprice = request.POST.get('price')
        productsize = request.POST.get('size')
        productweight = request.POST.get('weight')
        productavailability = request.POST.get('availability')
        productcolor = request.POST.get('color')
        productlocation = request.POST.get('location')
        productcategory = request.POST.get('category')
        productstatus = request.POST.get('status')
        productdescription = request.POST.get('description')

        #to prevent user form inputing any contact related info
        forbidden_words = ['facebook', 'instagram', 'whatsapp', 'twitter', 'youtube']

        
        if productimage == None:
            messages.error(request, 'Please upload an image in the first image input box!')

        else: 
            if (any(word in productdescription.lower() for word in forbidden_words)
                or any(char.isdigit() for char in productdescription) 
                or '@' in productdescription):
                messages.warning(request, 'Please DO NOT include any contact-related informations in your item description!')

            else:
                food_object = RestaurantFoodItem.objects.create(user=request.user, unique_id=unique_id, productname=productname, productimage=productimage,
                                                            productprice=productprice, productsize=productsize, productweight=productweight,
                                                            productimage2=productimage2, productimage3=productimage3, productimage4=productimage4,
                                                            productimage5=productimage5, productvideo=productvideo,
                                                            productavailability=productavailability, productcolor=productcolor,
                                                            productlocation=productlocation, productcategory=productcategory, productstatus=productstatus,
                                                            productdescription=productdescription)
                food_object.save();

                # create a general post
                post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='FoodItem')
                post_object.save();

                messages.success(request, 'Submitted Successfully! Your Item will be reviewed before being displayed on your page and other pages.')
    
        return redirect('restaurantprofile')

@prevent_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def orders(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    context = {**notification_context}
    return render(request, 'orders.html', context)

def contactareno(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first() 
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        message = request.POST.get('message')

        if phonenumber.startswith('0') or not phonenumber[1:].isdigit():
            messages.error(request, 'Please write your phone number correctly!, eg: +255****')
        else:
            message_object = ArenoMessage.objects.create(fullname=fullname, email=email, phonenumber=phonenumber, message=message)
            message_object.save();
            messages.success(request, 'Message sent successfully!')

            #sending sms and email 
            contactAreno(fullname, phonenumber, email)

    context = {**notification_context, 'arenodetails':arenodetails}
    return render(request, 'contactareno.html', context)

def offices(request):
    return render(request, 'offices.html')

def privacypolicy(request):
    arenodetails = ArenoContact.objects.all().first()
    arenoprivacys = ArenoPrivacyPolicy.objects.all().first()
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)

    context = {'arenodetails':arenodetails, 'arenoprivacys':arenoprivacys, **notification_context}
    return render(request, 'privacypolicy.html', context)

def rate(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    sliderreviews = ArenoRating.objects.all()[:20]
    reviews = ArenoRating.objects.all()
    arenodetails = ArenoContact.objects.all().first() 

    context = {**notification_context, 'sliderreviews':sliderreviews, 'reviews':reviews, 'arenodetails':arenodetails}
    return render(request, 'rate.html', context )

def postrate(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        ratings = request.POST.get('ratings')
        review = request.POST.get('review')

        review_object = ArenoRating.objects.create(fullname=fullname, email=email, ratings=ratings, review=review )
        review_object.save()
        messages.success(request, 'Review Submitted Successfully!')
        return redirect('rate')

def refundpolicies(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()
    arenorefunds = ArenoRefundPolicy.objects.all().first()

    context = {**notification_context, 'arenodetails':arenodetails, 'arenorefunds':arenorefunds}
    return render(request, 'refundpolicies.html', context)

def registerform(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()

    context = {**notification_context, 'arenodetails':arenodetails}
    return render(request, 'registerform.html', context)

def aboutus(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first()
    arenoabouts = ArenoAbout.objects.all()
    
    context = {**notification_context, 'arenodetails':arenodetails, 'arenoabouts':arenoabouts}
    return render(request, 'aboutus.html', context)

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def changepassword(request):
    user = request.user
    # Fetch notification data
    notification_context = notification_data(user)
    arenodetails = ArenoContact.objects.all().first() 
    if request.method == 'POST':
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
        elif not request.user.check_password(password):
            messages.info(request, "Please, Write your current password correctly!")
        else:

            #reset password
            user =request.user
            user.set_password(password1)
            update_session_auth_hash(request, user)
            user.save()
            
            messages.success(request, "Password Reset Successfully!.")
            return redirect('changepassword')

    context = {**notification_context, 'arenodetails':arenodetails}
    return render(request, 'changepassword.html', context )

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_account(request):
    try:
        sellerform = SellerRegistrationForm.objects.get(email=request.user)
    except SellerRegistrationForm.DoesNotExist:
        sellerform = None
        pass

    try:
        hostform = BookingHostForm.objects.get(email=request.user)
    except BookingHostForm.DoesNotExist:
        hostform = None
        pass

    if request.method == 'POST':
        # Delete user account
        user = request.user
        current_user = User.objects.filter(id=user.id)
        current_user.delete()

        if sellerform:
            sellerform.delete()
        
        if hostform:
            hostform.delete()
        messages.success(request, "Your account has been deleted successfully.")
      
        return redirect('index')  

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_profileimage(request):
    if request.method == 'POST':
        # Delete user account
        user = request.user
        profile = get_object_or_404(SellerProfile, user=user)
        profile.profileimage.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('shopsettings') 

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_customerprofileimage(request):
    if request.method == 'POST':
        # Delete user account
        user = request.user
        profile = get_object_or_404(CustomerProfile, user=user)
        profile.profileimage.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('customerprofile') 

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def rateuser(request):
    if request.method == 'POST':
        selleruser = request.POST.get('selleruser')
        rate = int (request.POST.get('rate'))

        if UserRate.objects.filter(user=request.user, selleruser=selleruser).exists():
            messages.error(request, 'Your rate has already been submitted. Thank You!')
            redirect_url = request.META.get('HTTP_REFERER')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect('index')
        else:
            rate_object = UserRate.objects.create(user=request.user, selleruser=selleruser, rate=rate)
            rate_object.save()
            messages.success(request, 'Thank You for rating this user. Your rate has been successfully submitted.')
            redirect_url = request.META.get('HTTP_REFERER')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect('index')







#booking
def booking(request):
    arenodetails = ArenoContact.objects.all().first()
    bookinghomepage = BookingMainPage.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass


    context = {'arenodetails': arenodetails, 'bookinghomepage':bookinghomepage, 'bookingads':bookingads, 'profile':profile}
    return render(request, 'booking.html', context)

def events(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    conferences = BookingEvent.objects.filter(category = 'Conferences', status='Approved')
    seminars = BookingEvent.objects.filter(category = 'Seminars', status='Approved')
    workshops = BookingEvent.objects.filter(category = 'WorkShops', status='Approved')
    festivals = BookingEvent.objects.filter(category = 'Festivals and Concerts', status='Approved')
    praises = BookingEvent.objects.filter(category = 'Praise and Worship', status='Approved')
    parties = BookingEvent.objects.filter(category = 'Parties and Ceremonies', status='Approved')
    others = BookingEvent.objects.filter(category = 'Other', status='Approved')
    events = BookingEvent.objects.filter(status='Approved')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass

    query = request.GET.get('query')
    if query:
        events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
        event_posts = []
        profile = None
        for event in events:
            try:
                profile = BookingHostProfile.objects.get(user=event.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            event_posts.append({
                'profile':profile,
                'event':event
                })

        context = {'arenodetails':arenodetails, 'events':events, 'event_posts':event_posts, 'query':query}
        return render(request, 'allevents.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'conferences':conferences, 'seminars':seminars,
                 'workshops':workshops, 'festivals':festivals, 'praises':praises, 'parties':parties, 'others':others, 'events':events, 'profile':profile}
    return render(request, 'events.html', context)

def eventpage(request, pk=None): 
    try:
        user=request.user
        event = BookingEvent.objects.get(pk=pk, status='Approved')
        postprofile = None
        userprofile = None
        # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=event.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
        # obtain current logged in user profile details
        try:
            userprofile = BookingHostProfile.objects.get(user=user) # for host user
        except BookingHostProfile.DoesNotExist:
            userprofile = None
            try:
                userprofile = CustomerProfile.objects.get(user=user) # for normal customer user
            except CustomerProfile.DoesNotExist:
                userprofile = None
                try:
                    userprofile = SellerProfile.objects.get(user=user) # for seller user
                except SellerProfile.DoesNotExist:
                    userprofile = None
                    pass
        except:
            pass
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'event':event, 'postprofile':postprofile, 'userprofile':userprofile}
    return render(request, 'eventpage.html', context)

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def eventpayment(request, pk=None):
    try:
        event = get_object_or_404(BookingEvent, pk=pk, status='Approved')
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'event':event}
    return render(request, 'eventpayment.html', context)

def allevents(request):
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        events = BookingEvent.objects.filter(status='Approved')

    #get host user instance

    event_posts = []
    profile = None
    for event in events:
        try:
            profile = BookingHostProfile.objects.get(user=event.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        event_posts.append({
            'profile':profile,
            'event':event
            })

    context = {'arenodetails':arenodetails, 'events':events, 'event_posts':event_posts, 'query':query}
    return render(request, 'allevents.html', context)

def eventhosts(request):
    hosts = BookingHostProfile.objects.filter(category = 'Events')

    query = request.GET.get('query')
    if query:
        hosts = BookingHostProfile.objects.filter(Q(company_name__icontains=query) | Q(bio__icontains=query) |
                                            Q(head_office_location__icontains=query) |
                                            Q(fullname__icontains=query), Q(category = 'Events'))
    

    context = {'hosts':hosts}
    return render(request, 'eventhosts.html', context)


def eventscategories(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    eventcats = BookingEventsCategory.objects.all().first()

    query = request.GET.get('query')
    if query:
        events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(venue__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))

        context = {'arenodetails':arenodetails, 'events':events,  'query':query,}
        return render(request, 'allevents.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'eventcats':eventcats}
    return render(request, 'eventscategories.html', context)

def eventsfilter(request, category):
    arenodetails = ArenoContact.objects.all().first()

    query = category
    if query:
        events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        events = BookingEvent.objects.filter(status='Approved')

    #get host user instance

    event_posts = []
    profile = None
    for event in events:
        try:
            profile = BookingHostProfile.objects.get(user=event.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        event_posts.append({
            'profile':profile,
            'event':event
            })

    context = {'arenodetails':arenodetails, 'events':events, 'event_posts':event_posts }
    return render(request, 'allevents.html', context)


def sports(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    footballs = BookingSports.objects.filter(category = 'Football & Soccer', status='Approved')
    baskets = BookingSports.objects.filter(category = 'Basket Ball', status='Approved')
    volleys = BookingSports.objects.filter(category = 'VolleyBall', status='Approved')
    tenniss = BookingSports.objects.filter(category = 'Table Tennis', status='Approved')
    swimmings = BookingSports.objects.filter(category = 'Swimming', status='Approved')
    boxings = BookingSports.objects.filter(category = 'Boxing', status='Approved')
    others = BookingSports.objects.filter(category = 'Other', status='Approved')
    sports = BookingSports.objects.filter(status='Approved')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass

    query = request.GET.get('query')
    if query:
        sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
        sport_posts = []
        profile = None
        for sport in sports:
            try:
                profile = BookingHostProfile.objects.get(user=sport.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            sport_posts.append({
                'profile':profile,
                'sport':sport
                })

        context = {'arenodetails':arenodetails, 'sports':sports, 'sport_posts':sport_posts, 'query':query}
        return render(request, 'allsports.html', context)


    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'footballs':footballs, 'baskets':baskets,
                'volleys':volleys, 'tenniss':tenniss, 'swimmings':swimmings, 'boxings':boxings, 'sports':sports, 'others':others, 'profile':profile}
    return render(request, 'sports.html', context)

def sportpage(request, pk=None):
    try:
        user=request.user
        event = BookingSports.objects.get(pk=pk, status='Approved')
        postprofile = None
        userprofile = None
        # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=event.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
        # obtain current logged in user profile details
        try:
            userprofile = BookingHostProfile.objects.get(user=user) # for host user
        except BookingHostProfile.DoesNotExist:
            userprofile = None
            try:
                userprofile = CustomerProfile.objects.get(user=user) # for normal customer user
            except CustomerProfile.DoesNotExist:
                userprofile = None
                try:
                    userprofile = SellerProfile.objects.get(user=user) # for seller user
                except SellerProfile.DoesNotExist:
                    userprofile = None
                    pass
        except:
            pass
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'event':event, 'postprofile':postprofile, 'userprofile':userprofile}
    return render(request, 'sportpage.html', context)

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def sportpayment(request, pk=None):
    try:
        event = get_object_or_404(BookingSports, pk=pk, status='Approved')
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'event':event}
    return render(request, 'sportpayment.html', context)

def allsports(request):
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        sports = BookingSports.objects.filter(status='Approved')

    #get host user instance

    sport_posts = []
    profile = None
    for sport in sports:
        try:
            profile = BookingHostProfile.objects.get(user=sport.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        sport_posts.append({
            'profile':profile,
            'sport':sport
            })

    context = {'arenodetails':arenodetails, 'sports':sports, 'sport_posts':sport_posts,  'query':query}
    return render(request, 'allsports.html', context)

def sporthosts(request):
    hosts = BookingHostProfile.objects.filter(category = 'Sports')

    query = request.GET.get('query')
    if query:
        hosts = BookingHostProfile.objects.filter(Q(company_name__icontains=query) | Q(bio__icontains=query) |
                                            Q(head_office_location__icontains=query) |
                                            Q(fullname__icontains=query), Q(category = 'Sports'))
    

    context = {'hosts':hosts}
    return render(request, 'sporthosts.html', context)

def sportscategories(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    sportcats = BookingSportsCategory.objects.all().first()

    query = request.GET.get('query')
    if query:
        sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
        sport_posts = []
        profile = None
        for sport in sports:
            try:
                profile = BookingHostProfile.objects.get(user=sport.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            sport_posts.append({
                'profile':profile,
                'sport':sport
                })

        context = {'arenodetails':arenodetails, 'sports':sports, 'sport_posts':sport_posts,  'query':query}
        return render(request, 'allsports.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'sportcats':sportcats}
    return render(request, 'sportscategories.html', context)

def sportsfilter(request, category):
    arenodetails = ArenoContact.objects.all().first()

    query = category
    if query:
        sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        sports = BookingSports.objects.filter(status='Approved')

    #get host user instance

    sport_posts = []
    profile = None
    for sport in sports:
        try:
            profile = BookingHostProfile.objects.get(user=sport.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        sport_posts.append({
            'profile':profile,
            'sport':sport
            })

    context = {'arenodetails':arenodetails, 'sports':sports, 'sport_posts':sport_posts,  'query':query}
    return render(request, 'allsports.html', context)


def adventures(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    city_tours = BookingAdventure.objects.filter(category = 'City Tour', status='Approved')
    national_parks = BookingAdventure.objects.filter(category = 'National Parks & Game reserves', status='Approved')
    hikings = BookingAdventure.objects.filter(category = 'Hiking & Climbing', status='Approved')
    historicals = BookingAdventure.objects.filter(category = 'Historical', status='Approved')
    beaches_coastals = BookingAdventure.objects.filter(category = 'Beaches & Coastal', status='Approved')
    others = BookingAdventure.objects.filter(category = 'Other', status='Approved')
    adventures = BookingAdventure.objects.filter(status='Approved')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass

    query = request.GET.get('query')
    if query:
        adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
        adventure_posts = []
        profile = None
        for adventure in adventures:
            try:
                profile = BookingHostProfile.objects.get(user=adventure.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            adventure_posts.append({
                'profile':profile,
                'adventure':adventure
                })

        context = {'arenodetails':arenodetails, 'adventures':adventures, 'adventure_posts':adventure_posts,  'query':query}
        return render(request, 'alladventures.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'city_tours':city_tours, 'national_parks':national_parks, 
                 'hikings':hikings, 'historicals':historicals, 'beaches_coastals':beaches_coastals, 'others':others, 'adventures':adventures, 'profile':profile }
    return render(request, 'adventure.html', context)

def adventurecategories(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    adventurecats = BookingAdventureCategory.objects.all().first()

    query = request.GET.get('query')
    if query:
        adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
        adventure_posts = []
        profile = None
        for adventure in adventures:
            try:
                profile = BookingHostProfile.objects.get(user=adventure.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            adventure_posts.append({
                'profile':profile,
                'adventure':adventure
                })

        context = {'arenodetails':arenodetails, 'adventures':adventures, 'adventure_posts':adventure_posts,  'query':query}
        return render(request, 'alladventures.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'adventurecats':adventurecats}
    return render(request, 'adventurecategories.html', context)

def adventuresfilter(request, category):
    arenodetails = ArenoContact.objects.all().first()

    query = category
    if query:
        adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    
    else:
        adventures = BookingAdventure.objects.filter(status='Approved')

    adventure_posts = []
    profile = None
    for adventure in adventures:
        try:
            profile = BookingHostProfile.objects.get(user=adventure.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        adventure_posts.append({
            'profile':profile,
            'adventure':adventure
            })

    context = {'arenodetails':arenodetails, 'adventures':adventures, 'adventure_posts':adventure_posts,  'query':query}
    return render(request, 'alladventures.html', context)

def alladventures(request):
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        adventures = BookingAdventure.objects.filter(status='Approved')

    #get host user instance

    adventure_posts = []
    profile = None
    for adventure in adventures:
        try:
            profile = BookingHostProfile.objects.get(user=adventure.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        adventure_posts.append({
            'profile':profile,
            'adventure':adventure
            })

    context = {'arenodetails':arenodetails, 'adventures':adventures, 'adventure_posts':adventure_posts,  'query':query}
    return render(request, 'alladventures.html', context)

def adventurehosts(request):
    hosts = BookingHostProfile.objects.filter(category = 'Adventure')

    query = request.GET.get('query')
    if query:
        hosts = BookingHostProfile.objects.filter(Q(company_name__icontains=query) | Q(bio__icontains=query) |
                                            Q(head_office_location__icontains=query) |
                                            Q(fullname__icontains=query), Q(category = 'Adventure'))
    

    context = {'hosts':hosts}
    return render(request, 'adventurehosts.html', context)


def adventurepage(request, pk=None):
    try:
        user=request.user
        adventure = BookingAdventure.objects.get(pk=pk, status='Approved')
        postprofile = None
        userprofile = None
        # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=adventure.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
        # obtain current logged in user profile details
        try:
            userprofile = BookingHostProfile.objects.get(user=user) # for host user
        except BookingHostProfile.DoesNotExist:
            userprofile = None
            try:
                userprofile = CustomerProfile.objects.get(user=user) # for normal customer user
            except CustomerProfile.DoesNotExist:
                userprofile = None
                try:
                    userprofile = SellerProfile.objects.get(user=user) # for seller user
                except SellerProfile.DoesNotExist:
                    userprofile = None
                    pass
        except:
            pass
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'adventure':adventure, 'postprofile':postprofile, 'userprofile':userprofile}
    return render(request, 'adventurepage.html', context)

def car_rental(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    standard_cars = BookingCarRental.objects.filter(category = 'Standard Car', status='Approved')
    suvs = BookingCarRental.objects.filter(category = 'SUV & 4WD', status='Approved')
    pick_ups = BookingCarRental.objects.filter(category = 'Pick-Up Truck', status='Approved')
    luxury_cars = BookingCarRental.objects.filter(category = 'Luxury Car', status='Approved')
    minivans = BookingCarRental.objects.filter(category = 'Mini-Van', status='Approved')
    safari_cars = BookingCarRental.objects.filter(category = 'Safari Car', status='Approved')
    mini_buses = BookingCarRental.objects.filter(category = 'Mini-Bus', status='Approved')
    others = BookingCarRental.objects.filter(category = 'Other', status='Approved')
    car_rentals = BookingCarRental.objects.filter(status='Approved')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass

    query = request.GET.get('query')
    if query:
        car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))

        car_rental_posts = []
        profile = None
        for car_rental in car_rentals:
            try:
                profile = BookingHostProfile.objects.get(user=car_rental.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            car_rental_posts.append({
                'profile':profile,
                'car_rental':car_rental
                })

        context = {'arenodetails':arenodetails, 'car_rentals':car_rentals, 'car_rentals':car_rentals, 'car_rental_posts':car_rental_posts,}
        return render(request, 'allcar_rentals.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'standard_cars':standard_cars, 'suvs':suvs, 'others':others,
               'pick_ups':pick_ups, 'luxury_cars':luxury_cars, 'minivans':minivans, 'safari_cars':safari_cars, 'mini_buses':mini_buses,
               'car_rentals':car_rentals, 'profile':profile }
    return render(request, 'car_rental.html', context)

def allcar_rentals(request):
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        car_rentals = BookingCarRental.objects.filter(status='Approved')

    #get host user instance

    car_rental_posts = []
    profile = None
    for car_rental in car_rentals:
        try:
            profile = BookingHostProfile.objects.get(user=car_rental.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        car_rental_posts.append({
            'profile':profile,
            'car_rental':car_rental
            })
    

    

    context = {'arenodetails':arenodetails, 'car_rentals':car_rentals, 'car_rental_posts':car_rental_posts,  'query':query}
    return render(request, 'allcar_rentals.html', context)

def car_rentalcategories(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    car_rentalcats = BookingCarRentalCategory.objects.all().first()

    query = request.GET.get('query')
    if query:
        car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))

        car_rental_posts = []
        profile = None
        for car_rental in car_rentals:
            try:
                profile = BookingHostProfile.objects.get(user=car_rental.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            car_rental_posts.append({
                'profile':profile,
                'car_rental':car_rental
                })

        context = {'arenodetails':arenodetails, 'car_rentals':car_rentals, 'car_rentals':car_rentals, 'car_rental_posts':car_rental_posts,}
        return render(request, 'allcar_rentals.html', context)
   

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'car_rentalcats':car_rentalcats}
    return render(request, 'car_rentalcategories.html', context)

def car_rentalsfilter(request, category):
    arenodetails = ArenoContact.objects.all().first()

    query = category
    if query:
        car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        car_rentals = BookingCarRental.objects.filter(status='Approved')

    car_rental_posts = []
    profile = None
    for car_rental in car_rentals:
        try:
            profile = BookingHostProfile.objects.get(user=car_rental.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        car_rental_posts.append({
            'profile':profile,
            'car_rental':car_rental
            })

    context = {'arenodetails':arenodetails, 'car_rentals':car_rentals, 'car_rentals':car_rentals, 'car_rental_posts':car_rental_posts,}
    return render(request, 'allcar_rentals.html', context)

def car_rentalhosts(request):
    hosts = BookingHostProfile.objects.filter(category = 'Car Rentals')

    query = request.GET.get('query')
    if query:
        hosts = BookingHostProfile.objects.filter(Q(company_name__icontains=query) | Q(bio__icontains=query) |
                                            Q(head_office_location__icontains=query) |
                                            Q(fullname__icontains=query), Q(category = 'Car Rentals'))
    

    context = {'hosts':hosts}
    return render(request, 'car_rentalhosts.html', context)


def car_rentalpage(request, pk=None):
    try:
        user=request.user
        car_rental = BookingCarRental.objects.get(pk=pk, status='Approved')
        postprofile = None
        userprofile = None
        # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=car_rental.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
        # obtain current logged in user profile details
        try:
            userprofile = BookingHostProfile.objects.get(user=user) # for host user
        except BookingHostProfile.DoesNotExist:
            userprofile = None
            try:
                userprofile = CustomerProfile.objects.get(user=user) # for normal customer user
            except CustomerProfile.DoesNotExist:
                userprofile = None
                try:
                    userprofile = SellerProfile.objects.get(user=user) # for seller user
                except SellerProfile.DoesNotExist:
                    userprofile = None
                    pass
        except:
            pass
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'car_rental':car_rental, 'postprofile':postprofile, 'userprofile':userprofile}
    return render(request, 'car_rentalpage.html', context)

def arenobnb(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    homes = BookingArenoBnb.objects.filter(category = 'Home', status='Approved')
    appartments = BookingArenoBnb.objects.filter(category = 'Appartment', status='Approved')
    hotels = BookingArenoBnb.objects.filter(category = 'Hotel', status='Approved')
    lodges = BookingArenoBnb.objects.filter(category = 'Lodge', status='Approved')
    villas = BookingArenoBnb.objects.filter(category = 'Villa', status='Approved')
    others = BookingArenoBnb.objects.filter(category = 'Other', status='Approved')
    arenobnbs = BookingArenoBnb.objects.filter(status='Approved')

    #get host user instance
    user = request.user
    profile = None
    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
        except BookingHostProfile.DoesNotExist:
            profile = None
            pass

    query = request.GET.get('query')
    if query:
        arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))

        arenobnb_posts = []
        for arenobnb in arenobnbs:
            profile = BookingHostProfile.objects.get(user=arenobnb.user)
            arenobnb_posts.append({
                'profile':profile,
                'arenobnb':arenobnb
                })

        context = {'arenodetails':arenodetails, 'arenobnbs':arenobnbs, 'arenobnb_posts':arenobnb_posts,}
        return render(request, 'allarenobnb.html', context)

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'homes':homes, 'appartments':appartments, 'others':others,
               'hotels':hotels, 'lodges':lodges, 'villas':villas, 'arenobnbs':arenobnbs, 'profile':profile }
    return render(request, 'arenobnb.html', context)

def allarenobnb(request):
    arenodetails = ArenoContact.objects.all().first()

    query = request.GET.get('query')
    if query:
        arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        arenobnbs = BookingArenoBnb.objects.filter(status='Approved')

    #get host user instance

    arenobnb_posts = []
    profile = None
    for arenobnb in arenobnbs:
        try:
            profile = BookingHostProfile.objects.get(user=arenobnb.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        arenobnb_posts.append({
            'profile':profile,
            'arenobnb':arenobnb
            })
    

    

    context = {'arenodetails':arenodetails, 'arenobnbs':arenobnbs, 'arenobnb_posts':arenobnb_posts,  'query':query}
    return render(request, 'allarenobnb.html', context)

def arenobnbcategories(request):
    arenodetails = ArenoContact.objects.all().first()
    bookingads = ArenoBookingAd.objects.all().order_by('?')
    arenobnbcats = BookingArenoBnbCategory.objects.all().first()

    query = request.GET.get('query')
    if query:
        arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))

        arenobnb_posts = []
        profile = None
        for arenobnb in arenobnbs:
            try:
                profile = BookingHostProfile.objects.get(user=arenobnb.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
            arenobnb_posts.append({
                'profile':profile,
                'arenobnb':arenobnb
                })

        context = {'arenodetails':arenodetails, 'arenobnbs':arenobnbs,  'arenobnb_posts':arenobnb_posts,}
        return render(request, 'allarenobnb.html', context)
   

    context = {'arenodetails': arenodetails, 'bookingads':bookingads, 'arenobnbcats':arenobnbcats}
    return render(request, 'arenobnbcategories.html', context)

def arenobnbsfilter(request, category):
    arenodetails = ArenoContact.objects.all().first()

    query = category
    if query:
        arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) |
                                            Q(category__icontains=query) |Q(location__icontains=query) |
                                            Q(organizer__icontains=query), Q(status='Approved'))
    else:
        arenobnbs = BookingArenoBnb.objects.filter(status='Approved')

    arenobnb_posts = []
    profile = None
    for arenobnb in arenobnbs:
        try:
            profile = BookingHostProfile.objects.get(user=arenobnb.user)
        except BookingHostProfile.DoesNotExist:
            profile = None
        arenobnb_posts.append({
            'profile':profile,
            'arenobnb':arenobnb
            })

    context = {'arenodetails':arenodetails, 'arenobnbs':arenobnbs, 'arenobnb_posts':arenobnb_posts,}
    return render(request, 'allarenobnb.html', context)

def arenobnbhosts(request):
    hosts = BookingHostProfile.objects.filter(category = 'Areno BNB')

    query = request.GET.get('query')
    if query:
        hosts = BookingHostProfile.objects.filter(Q(company_name__icontains=query) | Q(bio__icontains=query) |
                                            Q(head_office_location__icontains=query) |
                                            Q(fullname__icontains=query), Q(category = 'Areno BNB'))
    

    context = {'hosts':hosts}
    return render(request, 'arenobnbhosts.html', context)


def arenobnbpage(request, pk=None):
    try:
        user=request.user
        arenobnb = BookingArenoBnb.objects.get(pk=pk, status='Approved')
        postprofile = None
        userprofile = None
        # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=arenobnb.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
        # obtain current logged in user profile details
        try:
            userprofile = BookingHostProfile.objects.get(user=user) # for host user
        except BookingHostProfile.DoesNotExist:
            userprofile = None
            try:
                userprofile = CustomerProfile.objects.get(user=user) # for normal customer user
            except CustomerProfile.DoesNotExist:
                userprofile = None
                try:
                    userprofile = SellerProfile.objects.get(user=user) # for seller user
                except SellerProfile.DoesNotExist:
                    userprofile = None
                    pass
        except:
            pass
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'arenobnb':arenobnb, 'postprofile':postprofile, 'userprofile':userprofile}
    return render(request, 'arenobnbpage.html', context)

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def bookingfavourites(request):
    user = request.user
    posts = BookingFavourite.objects.filter(user = user)

    booking_posts = []
    profile = None
    for post in posts:
        try:
            event = BookingEvent.objects.get(unique_id = post.post_id)
            try:
                profile = BookingHostProfile.objects.get(user=event.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
        except BookingEvent.DoesNotExist:
            event = None
        try:
            sport = BookingSports.objects.get(unique_id = post.post_id)
            try:
                profile = BookingHostProfile.objects.get(user=sport.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
        except BookingSports.DoesNotExist:
            sport = None
        try:
            adventure = BookingAdventure.objects.get(unique_id = post.post_id)
            try:
                profile = BookingHostProfile.objects.get(user=adventure.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
        except BookingAdventure.DoesNotExist:
            adventure = None
        try:
            car_rental = BookingCarRental.objects.get(unique_id = post.post_id)
            try:
                profile = BookingHostProfile.objects.get(user=car_rental.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
        except BookingCarRental.DoesNotExist:
            car_rental = None
        try:
            arenobnb = BookingArenoBnb.objects.get(unique_id = post.post_id)
            try:
                profile = BookingHostProfile.objects.get(user=arenobnb.user)
            except BookingHostProfile.DoesNotExist:
                profile = None
        except BookingArenoBnb.DoesNotExist:
            arenobnb = None
        booking_posts.append({
            'profile':profile,
            'event':event,
            'sport':sport,
            'adventure':adventure,
            'car_rental':car_rental,
            'arenobnb':arenobnb,
            'post':post
        })
    

    context = {'posts':posts, 'booking_posts':booking_posts}
    return render(request, 'bookingfavourites.html', context)

@disabled_accounts
@login_required(login_url='login')
def deletefavourite(request, pk=None):
    try:
        post = BookingFavourite.objects.get(id=pk)
    except:
        post = None
        messages.error(request, 'Not Available!')
        return redirect('index')
   
    if request.method == 'POST':
        post.delete();
        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def adventurepayment(request, pk=None):
    try:
        event = get_object_or_404(BookingAdventure, pk=pk, status='Approved')
    except:
        messages.error(request, 'Not Available!')
        return redirect('index')

    context = {'event':event}
    return render(request, 'adventurepayment.html', context)

def nopage(request):
    return render(request, 'nopage.html')

def customer_required(request):
    return render(request, 'customer_required.html')

def unauthorized(request):
    return render(request, 'unauthorized.html')

def disabledaccounts(request):
    return render(request, 'disabledaccounts.html')

@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def tickets(request):
    arenodetails = ArenoContact.objects.all().first()

    context = {'arenodetails':arenodetails,}
    return render(request, 'tickets.html' , context)

def submitactivity(request):
    arenodetails = ArenoContact.objects.all().first()

    context = {'arenodetails':arenodetails,}
    return render(request, 'submitactivity.html', context)


def hostregister(request):
    arenodetails = ArenoContact.objects.all().first()

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        role = request.POST.get('role')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        website = request.POST.get('website')
        social_media = request.POST.get('social_media')
        category = request.POST.get('category')
        about = request.POST.get('about')
        host_id = request.FILES.get('host_id')
        licence = request.FILES.get('licence')
        other_document = request.FILES.get('otherdocument')

        if phonenumber.startswith ('0') or not phonenumber[1:].isdigit():
            messages.warning(request, 'Write your phone numbers correctly, eg: 255***')
            return redirect('hostregister')
        else:
            if (BookingHostForm.objects.filter(email=email).exists()) or (BookingHostProfile.objects.filter(email=email).exists()) or (User.objects.filter(email=email).exists()):
                    messages.info(request, 'Email  already exists! Please use another.')
                    return redirect('hostregister')
            else: 
                if (BookingHostForm.objects.filter(company_name=company_name).exists()) or (BookingHostProfile.objects.filter(company_name=company_name).exists()):
                    messages.error(request, 'Company Name  already exists!')
                    return redirect('hostregister')
                else:
                    host_profile = BookingHostForm.objects.create(fullname=fullname, company_name=company_name, head_office_location=location,
                                                                      company_role=role, phonenumber=phonenumber, email=email, socialmedia=social_media,
                                                                      website=website, category=category, about=about, host_ID=host_id, licence=licence,
                                                                      other_document=other_document)
                    host_profile.save()
                    messages.success(request, 'Form Successfully Submitted for review, You will be notified soon.')
                    HostForm(fullname, company_name, phonenumber, email)


    context = {'arenodetails':arenodetails}
    return render(request, 'hostregister.html', context)

@only_host
@disabled_accounts
@restrict_admin 
@login_required(login_url='login')
def hostprofile(request):
    user = request.user
    arenodetails = ArenoContact.objects.all().first()


    if user.is_authenticated:
        try:
            profile = BookingHostProfile.objects.get(user=user)
            if profile.category == None:
                error = f"User failed to access his/her host profile due to empty category in his profile: user - {user}"
                generalErrorReport(error, 4963, 'views.py')
            else:
                pass
                
        except BookingHostProfile.DoesNotExist:
            profile = None
            return redirect('index')
        

    followings = Following.objects.filter(user=user)
    following_count = followings.count()
    followers = Following.objects.filter(following_user=profile.user)
    followers_count = followers.count()
    #obtain following user details
    followings_users = []
    for following in followings:
        try:
            followingseller = SellerProfile.objects.get(id=following.following_user_id, email=following.following_user)
        except SellerProfile.DoesNotExist:
            followingseller = None

        try:
            followinghost = BookingHostProfile.objects.get(id=following.following_user_id, email=following.following_user)
        except BookingHostProfile.DoesNotExist:
            followinghost = None
        followings_users.append({
            'following':following,
            'followingseller':followingseller,
            'followinghost':followinghost
        })

    #initialize posts
    events = None
    event_count = None
    sports = None
    sport_count = None
    adventures = None
    adventure_count = None
    car_rentals = None
    car_rental_count = None
    arenobnbs = None
    arenobnb_count = None
    features = None
    
    # Host whose category is events
    try:
        events = BookingEvent.objects.filter(user=user, status='Approved')
        event_count = events.count()

        query = request.GET.get('query')
        if query:
            events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))
    except BookingEvent.DoesNotExist: 
        events = None
        event_count = None
        pass
    # Host whose category is sports
    try:
        sports = BookingSports.objects.filter(user=user, status='Approved')
        sport_count = sports.count()

        query = request.GET.get('query')
        if query:
            sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue_or_stadium__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingSports.DoesNotExist: 
        sports = None
        sport_count = None
        pass
    # Host whose category is adventure
    try:
        adventures = BookingAdventure.objects.filter(user=user, status='Approved')
        adventure_count = adventures.count()

        query = request.GET.get('query')
        if query:
            adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingAdventure.DoesNotExist: 
        adventures = None
        adventure_count = None
        pass
    # Host whose category is car rental
    try:
        car_rentals = BookingCarRental.objects.filter(user=user, status='Approved')
        car_rental_count = car_rentals.count()
        car_rentalcats = BookingCarRentalCategory.objects.all()

        query = request.GET.get('query')
        if query:
            car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingCarRental.DoesNotExist: 
        car_rentals = None
        car_rental_count = None
        pass
    # Host whose category is areno bnb
    try:
        arenobnbs = BookingArenoBnb.objects.filter(user=user, status='Approved')
        arenobnb_count = arenobnbs.count()
        features = BookingArenoBnbPropertyFeature.objects.all()

        query = request.GET.get('query')
        if query:
            arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingArenoBnb.DoesNotExist: 
        arenobnbs = None
        arenobnb_count = None
        features = None
        pass


    context = {'arenodetails':arenodetails,'profile':profile, 'followings':followings, 'followers_count':followers_count, 'following_count':following_count,
               'followings_users':followings_users, 'events':events, 'event_count':event_count, 'sports':sports, 'sport_count':sport_count,
               'adventures':adventures, 'adventure_count':adventure_count, 'car_rentals':car_rentals, 'car_rental_count':car_rental_count, 'car_rentalcats':car_rentalcats,
                'arenobnbs':arenobnbs, 'arenobnb_count':arenobnb_count, 'features':features }
    return render (request, 'hostprofile.html', context)

def host(request, pk):
    user = request.user
    arenodetails = ArenoContact.objects.all().first()

    try:
        profile = BookingHostProfile.objects.get(pk=pk)
    except BookingHostProfile.DoesNotExist:
        profile = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    following_true = None 
    if user.is_authenticated:
        following_true = Following.objects.filter(user=user, following_user=profile.user)
    else:
        following_true = None
    followings = Following.objects.filter(user=profile.user)
    following_count = followings.count()
    followers = Following.objects.filter(following_user=profile.user)
    followers_count = followers.count()
    
    rates = UserRate.objects.filter(selleruser = profile.user )

    #initialize posts
    events = None
    event_count = None
    sports = None
    sport_count = None
    adventures = None
    adventure_count = None
    car_rentals = None
    car_rental_count = None
    arenobnbs = None
    arenobnb_count = None
    features = None
    
    # Host whose category is events
    try:
        events = BookingEvent.objects.filter(user=profile.user, status='Approved')
        event_count = events.count()

        query = request.GET.get('query')
        if query:
            events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))
    except BookingEvent.DoesNotExist: 
        events = None
        event_count = None
        pass
    # Host whose category is sports
    try:
        sports = BookingSports.objects.filter(user=profile.user, status='Approved')
        sport_count = sports.count()

        query = request.GET.get('query')
        if query:
            sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue_or_stadium__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingSports.DoesNotExist: 
        sports = None
        sport_count = None
        pass
    # Host whose category is adventure
    try:
        adventures = BookingAdventure.objects.filter(user=profile.user, status='Approved')
        adventure_count = adventures.count()

        query = request.GET.get('query')
        if query:
            adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingAdventure.DoesNotExist: 
        adventures = None
        adventure_count = None
        pass
    # Host whose category is car rental
    try:
        car_rentals = BookingCarRental.objects.filter(user=profile.user, status='Approved')
        car_rental_count = car_rentals.count()

        query = request.GET.get('query')
        if query:
            car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingCarRental.DoesNotExist: 
        car_rentals = None
        car_rental_count = None
        pass
    # Host whose category is areno bnb
    try:
        arenobnbs = BookingArenoBnb.objects.filter(user=profile.user, status='Approved')
        arenobnb_count = arenobnbs.count()
        features = BookingArenoBnbPropertyFeature.objects.all()

        query = request.GET.get('query')
        if query:
            arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Approved'))

    except BookingArenoBnb.DoesNotExist: 
        arenobnbs = None
        arenobnb_count = None
        features = None
        pass


    context = {'arenodetails':arenodetails,'profile':profile, 'following_true':following_true, 'followers_count':followers_count, 'rates':rates, 'followings':followings, 'following_count':following_count,
               'events':events, 'event_count':event_count, 'sports':sports, 'sport_count':sport_count,
               'adventures':adventures, 'adventure_count':adventure_count, 'car_rentals':car_rentals, 'car_rental_count':car_rental_count,
                'arenobnbs':arenobnbs, 'arenobnb_count':arenobnb_count, 'features':features }
    return render (request, 'host.html', context)

@only_host
@disabled_accounts
@restrict_admin 
@login_required(login_url='login')
def hostpendingposts(request):
    user = request.user

    try:
        profile = BookingHostProfile.objects.get(user=user)
    except BookingHostProfile.DoesNotExist:
        profile = None
        messages.error(request, 'Not Available!')
        return redirect('index')
        
  
    #initialize posts
    events = None
    event_count = None
    sports = None
    sport_count = None
    adventures = None
    adventure_count = None
    car_rentals = None
    car_rental_count = None
    arenobnbs = None
    arenobnb_count = None
    
    # Host whose category is events
    try:
        events = BookingEvent.objects.filter(user=profile.user, status='Pending')
        event_count = events.count()

        query = request.GET.get('query')
        if query:
            events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue__icontains=query) | Q(organizer__icontains=query), Q(status='Pending'))
    except BookingEvent.DoesNotExist: 
        events = None
        event_count = None
        pass
    # Host whose category is sports
    try:
        sports = BookingSports.objects.filter(user=profile.user, status='Pending')
        sport_count = sports.count()

        query = request.GET.get('query')
        if query:
            sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue_or_stadium__icontains=query) | Q(organizer__icontains=query), Q(status='Pending'))

    except BookingSports.DoesNotExist: 
        sports = None
        sport_count = None
        pass
    # Host whose category is adventure
    try:
        adventures = BookingAdventure.objects.filter(user=profile.user, status='Pending')
        adventure_count = adventures.count()

        query = request.GET.get('query')
        if query:
            adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Pending'))

    except BookingAdventure.DoesNotExist: 
        adventures = None
        adventure_count = None
        pass
    # Host whose category is car rental
    try:
        car_rentals = BookingCarRental.objects.filter(user=profile.user, status='Pending')
        car_rental_count = car_rentals.count()

        query = request.GET.get('query')
        if query:
            car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Pending'))

    except BookingCarRental.DoesNotExist: 
        car_rentals = None
        car_rental_count = None
        pass
    # Host whose category is areno bnb
    try:
        arenobnbs = BookingArenoBnb.objects.filter(user=profile.user, status='Pending')
        arenobnb_count = arenobnbs.count()

        query = request.GET.get('query')
        if query:
            arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Pending'))

    except BookingArenoBnb.DoesNotExist: 
        arenobnbs = None
        arenobnb_count = None
        pass


    context = { 'profile':profile,
               'events':events, 'event_count':event_count, 'sports':sports, 'sport_count':sport_count,
               'adventures':adventures, 'adventure_count':adventure_count, 'car_rentals':car_rentals, 'car_rental_count':car_rental_count,
                'arenobnbs':arenobnbs, 'arenobnb_count':arenobnb_count}
    return render (request, 'hostpendingposts.html', context)

@only_host
@disabled_accounts
@restrict_admin 
@login_required(login_url='login')
def hostdeclinedposts(request):
    user = request.user

    try:
        profile = BookingHostProfile.objects.get(user=user)
    except BookingHostProfile.DoesNotExist:
        profile = None
        messages.error(request, 'Not Available!')
        return redirect('index')
        
  
    #initialize posts
    events = None
    event_count = None
    sports = None
    sport_count = None
    adventures = None
    adventure_count = None
    car_rentals = None
    car_rental_count = None
    arenobnbs = None
    arenobnb_count = None
    
    # Host whose category is events
    try:
        events = BookingEvent.objects.filter(user=profile.user, status='Declined')
        event_count = events.count()

        query = request.GET.get('query')
        if query:
            events = BookingEvent.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue__icontains=query) | Q(organizer__icontains=query), Q(status='Declined'))
    except BookingEvent.DoesNotExist: 
        events = None
        event_count = None
        pass
    # Host whose category is sports
    try:
        sports = BookingSports.objects.filter(user=profile.user, status='Declined')
        sport_count = sports.count()

        query = request.GET.get('query')
        if query:
            sports = BookingSports.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) |Q(venue_or_stadium__icontains=query) | Q(organizer__icontains=query), Q(status='Declined'))

    except BookingSports.DoesNotExist: 
        sports = None
        sport_count = None
        pass
    # Host whose category is adventure
    try:
        adventures = BookingAdventure.objects.filter(user=profile.user, status='Declined')
        adventure_count = adventures.count()

        query = request.GET.get('query')
        if query:
            adventures = BookingAdventure.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Declined'))

    except BookingAdventure.DoesNotExist: 
        adventures = None
        adventure_count = None
        pass
    # Host whose category is car rental
    try:
        car_rentals = BookingCarRental.objects.filter(user=profile.user, status='Declined')
        car_rental_count = car_rentals.count()

        query = request.GET.get('query')
        if query:
            car_rentals = BookingCarRental.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Declined'))

    except BookingCarRental.DoesNotExist: 
        car_rentals = None
        car_rental_count = None
        pass
    # Host whose category is areno bnb
    try:
        arenobnbs = BookingArenoBnb.objects.filter(user=profile.user, status='Declined')
        arenobnb_count = arenobnbs.count()

        query = request.GET.get('query')
        if query:
            arenobnbs = BookingArenoBnb.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query) | Q(organizer__icontains=query), Q(status='Declined'))

    except BookingArenoBnb.DoesNotExist: 
        arenobnbs = None
        arenobnb_count = None
        pass


    context = { 'profile':profile,
               'events':events, 'event_count':event_count, 'sports':sports, 'sport_count':sport_count,
               'adventures':adventures, 'adventure_count':adventure_count, 'car_rentals':car_rentals, 'car_rental_count':car_rental_count,
                'arenobnbs':arenobnbs, 'arenobnb_count':arenobnb_count}
    return render (request, 'hostdeclinedposts.html', context)

@disabled_accounts
@restrict_admin 
@login_required(login_url='login')
def savebookingpost(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        if BookingFavourite.objects.filter(user=request.user, post_id=post_id).exists():
            messages.info(request, 'Post is already added to favourites.')
            redirect_url = request.META.get('HTTP_REFERER')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect('index')
        else:
            post_object = BookingFavourite.objects.create(user=request.user, post_id=post_id)
            post_object.save()
            messages.info(request, 'Post successfully added to favourites.')
            redirect_url = request.META.get('HTTP_REFERER')
            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect('index')


@disabled_accounts
@login_required(login_url='login')
def deleteeventpost(request, pk=None):
    try:
        eventpost = get_object_or_404(BookingEvent, id=pk)
    except:
        eventpost = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    try:
        generalpost = GeneralPost.objects.get(Post_Id=eventpost.unique_id)
    except:
        generalpost = None

    if request.method == 'POST':
        eventpost.delete();
        if generalpost:
            generalpost.delete()
        
        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@disabled_accounts
@login_required(login_url='login')
def deletesportpost(request, pk=None):
    try:
        sportpost = get_object_or_404(BookingSports, id=pk)
    except:
        sportpost = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    try:
        generalpost = get_object_or_404(GeneralPost, Post_Id=sportpost.unique_id)
    except:
        generalpost = None

    if request.method == 'POST':
        sportpost.delete();
        if generalpost:
            generalpost.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@disabled_accounts
@login_required(login_url='login')
def deleteadventurepost(request, pk=None):
    try:
        adventurepost = get_object_or_404(BookingAdventure, id=pk)
    except:
        adventurepost = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    try:
        generalpost = get_object_or_404(GeneralPost, Post_Id=adventurepost.unique_id)
    except:
        generalpost = None

    if request.method == 'POST':
        adventurepost.delete();
        if generalpost:
            generalpost.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@disabled_accounts
@login_required(login_url='login')
def deletecar_rentalpost(request, pk=None):
    try:
        car_rentalpost = get_object_or_404(BookingCarRental, id=pk)
    except:
        car_rentalpost = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    try:
        generalpost = get_object_or_404(GeneralPost, Post_Id=car_rentalpost.unique_id)
    except:
        generalpost = None

    if request.method == 'POST':
        car_rentalpost.delete();
        if generalpost:
            generalpost.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@disabled_accounts
@login_required(login_url='login')
def deletearenobnbpost(request, pk=None):
    try:
        arenobnbpost = get_object_or_404(BookingArenoBnb, id=pk)
    except:
        arenobnbpost = None
        messages.error(request, 'Not Available!')
        return redirect('index')
    try:
        generalpost = get_object_or_404(GeneralPost, Post_Id=arenobnbpost.unique_id)
    except:
        generalpost = None

    if request.method == 'POST':
        arenobnbpost.delete();
        if generalpost:
            generalpost.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            pass

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editbookingpost(request, pk):
    user = request.user
    arenodetails = ArenoContact.objects.all().first() 
    try:
        profile = get_object_or_404(BookingHostProfile, user=user)
    except:
        profile = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    post = None
    features = None

    try:
        post = BookingEvent.objects.get(user=user, status='Approved', pk=pk)
    except BookingEvent.DoesNotExist:
        post = None
        try:
            post = BookingSports.objects.get(user=user, status='Approved', pk=pk)
        except BookingSports.DoesNotExist:
            post = None
            try:
                post = BookingAdventure.objects.get(user=user, status='Approved', pk=pk)
            except BookingAdventure.DoesNotExist:
                post = None
                try:
                    post = BookingCarRental.objects.get(user=user, status='Approved', pk=pk)
                    car_rentalcats = BookingCarRentalCategory.objects.all()
                except BookingCarRental.DoesNotExist:
                    post = None
                    try:
                        post = BookingArenoBnb.objects.get(user=user, status='Approved', pk=pk)
                        features = BookingArenoBnbPropertyFeature.objects.all()
                    except BookingArenoBnb.DoesNotExist:
                        post = None
                        features = None
    except:
        post = None
        messages.error(request, 'Not Available!')
        return redirect('index')

    
    context = {'arenodetails':arenodetails, 'post':post, 'profile':profile, 'features':features, 'car_rentalcats':car_rentalcats }

    return render(request, 'editbookingpost.html', context)

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editeventpost(request, pk):
    user = request.user
    try:
        event = get_object_or_404(BookingEvent, user=user, status='Approved', pk=pk)
        if request.method == 'POST':
            event.title = request.POST.get('title')
            event.submitted_category = request.POST.get('category')
            event.venue = request.POST.get('venue')
            event.location = request.POST.get('location','')
            event.date = request.POST.get('date','')
            event.upto = request.POST.get('upto','')
            event.time = request.POST.get('time','')
            event.timeupto = request.POST.get('timeupto','')
            event.contact_1 = request.POST.get('contact1','')
            event.contact_2 = request.POST.get('contact2','')
            event.email = request.POST.get('email','')
            event.regular_price = request.POST.get('regularprice','')
            event.vip_price = request.POST.get('vipprice','')
            event.vvip_price = request.POST.get('vvipprice','')

            event.save()
            return redirect ('hostprofile')
    except BookingEvent.DoesNotExist:
        event = None
        pass
        error = f"Failed to edit event post in host post editing page view: user - {user}. This may also be due to the editbookingpost python blocks to only display the required saving route per each category. please check the html too."
        generalErrorReport(error, 5148, 'views.py')
        
        return redirect ('hostprofile')
    
@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editsportpost(request, pk):
    user = request.user
    try:
        sport = get_object_or_404(BookingSports, user=user, status='Approved', pk=pk)
        if request.method == 'POST':
            sport.title = request.POST.get('title')
            sport.submitted_category = request.POST.get('category')
            sport.venue_or_stadium = request.POST.get('venue')
            sport.location = request.POST.get('location','')
            sport.date = request.POST.get('date','')
            sport.upto = request.POST.get('upto','')
            sport.time = request.POST.get('time','')
            sport.timeupto = request.POST.get('timeupto','')
            sport.contact_1 = request.POST.get('contact1','')
            sport.contact_2 = request.POST.get('contact2','')
            sport.email = request.POST.get('email','')
            sport.regular_price = request.POST.get('regularprice','')
            sport.vip_price = request.POST.get('vipprice','')
            sport.vvip_price = request.POST.get('vvipprice','')

            sport.save()
            return redirect ('hostprofile')
    except BookingSports.DoesNotExist:
        sport = None
        pass
        error = f"Failed to edit sport post in host post editing page view: user - {user}. This may also be due to the editbookingpost python blocks to only display the required saving route per each category. please check the html too."
        generalErrorReport(error, 5189, 'views.py')
        
        return redirect ('hostprofile')

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editadventurepost(request, pk):
    user = request.user
    try:
        adventure = get_object_or_404(BookingAdventure, user=user, status='Approved', pk=pk)
        if request.method == 'POST':
            adventure.title = request.POST.get('title')
            adventure.submitted_category = request.POST.get('category')
            adventure.location = request.POST.get('location','')
            adventure.date = request.POST.get('date','')
            adventure.upto = request.POST.get('upto','')
            adventure.time = request.POST.get('time','')
            adventure.timeupto = request.POST.get('timeupto','')
            adventure.contact_1 = request.POST.get('contact1','')
            adventure.contact_2 = request.POST.get('contact2','')
            adventure.email = request.POST.get('email','')
            adventure.regular_price = request.POST.get('regularprice','')
            adventure.vip_price = request.POST.get('vipprice','')
            adventure.vvip_price = request.POST.get('vvipprice','')

            adventure.save()
            return redirect ('hostprofile')
    except BookingAdventure.DoesNotExist:
        adventure = None
        pass
        error = f"Failed to edit adventure post in host post editing page view: user - {user}. This may also be due to the editbookingpost python blocks to only display the required saving route per each category. please check the html too."
        generalErrorReport(error, 5189, 'views.py')
        
        return redirect ('hostprofile')

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editcar_rentalpost(request, pk):

    # DONT DISRUPT THIS CODE unless you understand it well

    user = request.user
    try:
        car_rental = get_object_or_404(BookingCarRental, user=user, status='Approved', pk=pk)
        if request.method == 'POST':
            car_rental.name = request.POST.get('name')
            car_rental.submitted_category = request.POST.get('category')
            car_rental.engine_size = request.POST.get('engine_size')
            car_rental.mileage = request.POST.get('mileage')
            car_rental.year = request.POST.get('year')
            car_rental.wheeldrive = request.POST.get('wheeldrive')
            car_rental.transmission = request.POST.get('transmission')
            car_rental.fuel_type = request.POST.get('fuel_type')
            car_rental.no_of_doors = request.POST.get('no_of_doors')
            car_rental.no_of_seats = request.POST.get('no_of_seats')
            car_rental.exterior_color = request.POST.get('exterior_color')
            service1 = request.POST.get('service_1')
            if service1:
                car_rental.service_1 = service1
            else: # to remolve the service object in database if user selects as to edit
                service_edit_1 = request.POST.get('service_edit_1')
                if service_edit_1:
                    car_rental.service_1 = None
                else:
                    pass

            service2= request.POST.get('service_2')
            if service2:
                car_rental.service_2 = service2
            else: # to remolve the service object in database if user selects as to edit
                service_edit_2 = request.POST.get('service_edit_2')
                if service_edit_2:
                    car_rental.service_2 = None
                else:
                    pass

            service3 = request.POST.get('service_3')
            if service3:
                car_rental.service_3 = service3
            else: # to remolve the service object in database if user selects as to edit
                service_edit_3 = request.POST.get('service_edit_3')
                if service_edit_3:
                    car_rental.service_3 = None
                else:
                    pass

            service4 = request.POST.get('service_4')
            if service4:
                car_rental.service_4 = service4
            else: # to remolve the service object in database if user selects as to edit
                service_edit_4 = request.POST.get('service_edit_4')
                if service_edit_4:
                    car_rental.service_4 = None
                else:
                    pass

            service5 = request.POST.get('service_5')
            if service5:
                car_rental.service_5 = service5
            else: # to remolve the service object in database if user selects as to edit
                service_edit_5 = request.POST.get('service_edit_5')
                if service_edit_5:
                    car_rental.service_5 = None
                else:
                    pass
            
            service6 = request.POST.get('service_6')
            if service6:
                car_rental.service_6 = service6
            else: # to remolve the service object in database if user selects as to edit
                service_edit_6 = request.POST.get('service_edit_6')
                if service_edit_6:
                    car_rental.service_6 = None
                else:
                    pass

            service7 = request.POST.get('service_7')
            if service7:
                car_rental.service_7 = service7
            else: # to remolve the service object in database if user selects as to edit
                service_edit_7 = request.POST.get('service_edit_7')
                if service_edit_7:
                    car_rental.service_7 = None
                else:
                    pass

            service8 = request.POST.get('service_8')
            if service8:
                car_rental.service_8 = service8
            else: # to remolve the service object in database if user selects as to edit
                service_edit_8 = request.POST.get('service_edit_8')
                if service_edit_8:
                    car_rental.service_8 = None
                else:
                    pass

            car_rental.nationality = request.POST.get('nationality')
            car_rental.availability = request.POST.get('availability')
            car_rental.location = request.POST.get('location','')
            car_rental.vehicle_type_or_brand = request.POST.get('brand','')
            car_rental.contact_1 = request.POST.get('contact1','')
            car_rental.contact_2 = request.POST.get('contact2','')
            car_rental.email = request.POST.get('email','')
            car_rental.price = request.POST.get('price','')

            car_rental.save()
            return redirect ('hostprofile')
    except BookingCarRental.DoesNotExist:
        car_rental = None
        pass
        error = f"Failed to edit car rentale post in host post editing page view: user - {user}. This may also be due to the editbookingpost python blocks to only display the required saving route per each category. please check the html too."
        generalErrorReport(error, 5312, 'views.py')
        
        return redirect ('hostprofile')

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def editarenobnbpost(request, pk):
    user = request.user
    try:
        arenobnb = get_object_or_404(BookingArenoBnb, user=user, status='Approved', pk=pk)
        if request.method == 'POST':
            arenobnb.name = request.POST.get('name')
            arenobnb.submitted_category = request.POST.get('category')
            #obtain the id of that foreign key item from property feature and save it
            feature_id = request.POST.get('feature')
            new_feature = get_object_or_404(BookingArenoBnbPropertyFeature, id = feature_id )
            arenobnb.property_feature = new_feature

            arenobnb.location = request.POST.get('location','')
            arenobnb.availability = request.POST.get('availability','')
            arenobnb.contact_1 = request.POST.get('contact1','')
            arenobnb.contact_2 = request.POST.get('contact2','')
            arenobnb.email = request.POST.get('email','')
            arenobnb.price = request.POST.get('price','')
            arenobnb.description = request.POST.get('description','')


            arenobnb.save()
            return redirect ('hostprofile')
    except BookingArenoBnb.DoesNotExist:
        arenobnb = None
        pass
        error = f"Failed to edit areno bnb post in host post editing page view: user - {user}. This may also be due to the editbookingpost python blocks to only display the required saving route per each category. please check the html too."
        generalErrorReport(error, 5492, 'views.py')
        
        return redirect ('hostprofile')

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def arenobnbrequest(request, pk=None):
    try:
        arenobnb = get_object_or_404(BookingArenoBnb, pk = pk)
    except BookingArenoBnb.DoesNotExist:
        arenobnb = None
        messages.error(request, 'Not Available!')
        return redirect('index')
        
    if request.method == 'POST':
        user = request.user
        fullname = request.POST.get('fullname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        check_in_date = request.POST.get('checkin')
        check_out_date = request.POST.get('checkout')
        host = request.POST.get('host')
        post_name = request.POST.get('post_name')
        post_id = request.POST.get('post_id')

        if phonenumber.startswith ('0') or not phonenumber[1:].isdigit():
            messages.warning(request, 'Write your phone numbers correctly, eg: 255***')
            return redirect ('arenobnbpage', pk)
        else:
            request_object = BookingRequest.objects.create(user=user, fullname=fullname, phonenumber=phonenumber,
                                                            email=email, check_in_date=check_in_date, check_out_date=check_out_date, 
                                                            host=host, post_name=post_name, post_id=post_id )
            request_object.save()
            arenoBnbRequest(fullname, phonenumber, email, arenobnb.name)
            messages.success(request, 'Successfully Submitted, You will be notified soon.')
            return redirect ('arenobnbpage', pk)

@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def car_rentalrequest(request, pk=None):
    try:
        car_rental = get_object_or_404(BookingCarRental, pk = pk)
    except BookingCarRental.DoesNotExist:
        car_rental = None
        messages.error(request, 'Not Available!')
        return redirect('index')
        
    if request.method == 'POST':
        user = request.user
        fullname = request.POST.get('fullname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        date = request.POST.get('date')
        description = request.POST.get('description')
        host = request.POST.get('host')
        post_name = request.POST.get('post_name')
        post_id = request.POST.get('post_id')

        if phonenumber.startswith ('0') or not phonenumber[1:].isdigit():
            messages.warning(request, 'Write your phone numbers correctly, eg: 255***')
            return redirect ('car_rentalpage', pk)
        else:
            request_object = BookingCarRequest.objects.create(user=user, fullname=fullname, phonenumber=phonenumber,
                                                            email=email, date=date, description=description, host=host, 
                                                            post_name=post_name, post_id=post_id  )
            request_object.save()
            arenoBnbRequest(fullname, phonenumber, email, car_rental.name)
            messages.success(request, 'Successfully Submitted, You will be notified soon.')
            return redirect ('car_rentalpage', pk)
    
@only_host
@restrict_admin 
@disabled_accounts
@login_required(login_url='login')
def arenobookingquestion(request, pk=None):
    try:
        post = BookingArenoBnb.objects.get(pk = pk)
    except BookingArenoBnb.DoesNotExist:
        post = None
        try:
            post = BookingCarRental.objects.get(pk = pk)
        except BookingCarRental.DoesNotExist:
            post = None
            try:
                post = BookingAdventure.objects.get(pk = pk)
            except BookingAdventure.DoesNotExist:
                post = None
                try:
                    post = BookingSports.objects.get(pk = pk)
                except BookingSports.DoesNotExist:
                    post = None
                    try:
                        post = BookingEvent.objects.get(pk = pk)
                    except BookingEvent.DoesNotExist:
                        post = None
                        messages.error(request, 'Not Available!')
                        return redirect('index')
                    
    if post:
        if request.method == 'POST':
            user = request.user
            fullname = request.POST.get('fullname')
            phonenumber = request.POST.get('phonenumber')
            email = request.POST.get('email')
            question = request.POST.get('question')
            booking_title = request.POST.get('post')
            post_id = request.POST.get('post_id')
            post_category = request.POST.get('post_category')
            host = request.POST.get('host')

            if phonenumber.startswith ('0') or not phonenumber[1:].isdigit():
                redirect_url = request.META.get('HTTP_REFERER')
                if redirect_url:
                    messages.warning(request, 'Write your phone numbers correctly, eg: 255***')
                    return redirect (redirect_url, pk)
                else:
                    return redirect('index')
            else:
                question_object = BookingQuestion.objects.create(user=user, fullname=fullname, phonenumber=phonenumber, post_category=post_category,
                                                                email=email, question=question, booking_title=booking_title, host=host, post_id=post_id)
                question_object.save()
                redirect_url = request.META.get('HTTP_REFERER')
                if redirect_url:
                    messages.success(request, 'Successfully Submitted, You will be replied soon.')
                    return redirect (redirect_url, pk)
                else:
                    return redirect('index')
    else:
        messages.error(request, 'Not Available!')
        return redirect('index')


@only_host
@disabled_accounts
@restrict_admin 
@login_required(login_url='login')
def hostsettings(request):
    user = request.user
    arenodetails = ArenoContact.objects.all().first() 
    rates = UserRate.objects.filter(selleruser = user )

    profile = BookingHostProfile.objects.get(user=user)
    if profile.category == 'Events':
        try:
            # get event host posts details for dashboard counter
            activeitems = BookingEvent.objects.filter(user=user, status='Approved')
            activecounter = activeitems.count()
            pendingitems = BookingEvent.objects.filter(user=user, status='Pending')
            pendingcounter = pendingitems.count()
            declineditems = BookingEvent.objects.filter(user=user, status='Declined')
            declinedcounter = declineditems.count()
        except BookingEvent.DoesNotExist:
            pass
    elif profile.category == 'Sports':
        try:
            # get sports host posts details for dashboard counter
            activeitems = BookingSports.objects.filter(user=user, status='Approved')
            activecounter = activeitems.count()
            pendingitems = BookingSports.objects.filter(user=user, status='Pending')
            pendingcounter = pendingitems.count()
            declineditems = BookingSports.objects.filter(user=user, status='Declined')
            declinedcounter = declineditems.count()
        except BookingSports.DoesNotExist:
            pass
    elif profile.category == 'Adventure':
        try:
            # get adventure host posts details for dashboard counter
            activeitems = BookingAdventure.objects.filter(user=user, status='Approved')
            activecounter = activeitems.count()
            pendingitems = BookingAdventure.objects.filter(user=user, status='Pending')
            pendingcounter = pendingitems.count()
            declineditems = BookingAdventure.objects.filter(user=user, status='Declined')
            declinedcounter = declineditems.count()
        except BookingAdventure.DoesNotExist:
            pass
    elif profile.category == 'Car Rentals':
        try:
            # get car rental host posts details for dashboard counter
            activeitems = BookingCarRental.objects.filter(user=user, status='Approved')
            activecounter = activeitems.count()
            pendingitems = BookingCarRental.objects.filter(user=user, status='Pending')
            pendingcounter = pendingitems.count()
            declineditems = BookingCarRental.objects.filter(user=user, status='Declined')
            declinedcounter = declineditems.count()
        except BookingCarRental.DoesNotExist:
            pass
    elif profile.category == 'Areno BNB':
        try:
            # get car rental host posts details for dashboard counter
            activeitems = BookingArenoBnb.objects.filter(user=user, status='Approved')
            activecounter = activeitems.count()
            pendingitems = BookingArenoBnb.objects.filter(user=user, status='Pending')
            pendingcounter = pendingitems.count()
            declineditems = BookingArenoBnb.objects.filter(user=user, status='Declined')
            declinedcounter = declineditems.count()
        except BookingArenoBnb.DoesNotExist:
            pass
    else:
        pass
        activecounter = None
        pendingcounter = None
        declinedcounter = None

    if request.method == 'POST':

        profileimage = request.FILES.get('profileimage')
        if profileimage:
            profile.profileimage = profileimage

        profile.head_office_location = request.POST.get('location', '')
        profile.phonenumber = request.POST.get('phonenumber', '')
        profile.bio = request.POST.get('bio', '')


        #prevent user to input any contact related items
        forbidden_words = ['facebook', 'instagram', 'whatsapp', 'twitter', 'youtube']

        if (any(char.isdigit() for char in profile.bio) 
            or '@' in profile.bio
            or any(word in profile.bio.lower() for word in forbidden_words)):
            messages.warning(request, 'Please DO NOT include numbers and any other contact-related informations in your biography!')
            return redirect('hostsettings')
        else:
            if profile.phonenumber.startswith ('0') or not profile.phonenumber[1:].isdigit() :
                messages.error(request, 'Write your phone number correctly, eg: 255***')
                return redirect('hostsettings')
            else:
                profile.save();
    
        return redirect ('hostprofile')
    
    context = {'arenodetails':arenodetails, 'rates':rates, 'profile':profile, 'activecounter':activecounter, 'pendingcounter':pendingcounter, 'declinedcounter':declinedcounter,}

    return render(request, 'hostsettings.html', context)

@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def hostpostevent(request):
    user = request.user
    profile = BookingHostProfile.objects.get(user=user)

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = profile.company_name
        title = request.POST.get('title')
        category = request.POST.get('category')
        venue = request.POST.get('venue')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        time = request.POST.get('time')
        timeupto = request.POST.get('timeupto')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        video = request.FILES.get('video')
        status = 'Pending'

        
        
        if image == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            event_object = BookingEvent.objects.create(user=user, unique_id=unique_id, title=title, organizer=organizer, upto=upto,
                                                    image=image, submitted_category=category, venue=venue, date=date, time=time, timeupto=timeupto, contact_1=contact_1,
                                                    contact_2=contact_2, email=email, regular_price=regular_price, status=status, 
                                                    image2=image2, image3=image3, image4=image4, image5=image5, video=video,
                                                    vip_price=vip_price, vvip_price=vvip_price, location=location,  description=description)
            
            event_object.save();

            # create a general post
            post_object = GeneralPost.objects.create(user=request.user, Post_Id=unique_id, ItemName=title,
                                                    Location=location, Description=description, Type='Event')
            post_object.save();

            messages.success(request, 'Submitted Successfully! Your Post will be reviewed before being displayed on your page and other pages.')
    
        return redirect('hostprofile')

@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def hostpostsport(request):
    user = request.user
    profile = BookingHostProfile.objects.get(user=user)

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = profile.company_name
        title = request.POST.get('title')
        category = request.POST.get('category')
        venue = request.POST.get('venue')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        time = request.POST.get('time')
        timeupto = request.POST.get('timeupto')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        video = request.FILES.get('video')
        status = 'Pending'

        
        
        if image == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            sport_object = BookingSports.objects.create(user=user, unique_id=unique_id, title=title, organizer=organizer, upto=upto,
                                                    image=image, submitted_category=category, venue_or_stadium=venue, date=date, time=time, timeupto=timeupto, contact_1=contact_1,
                                                    contact_2=contact_2, email=email, regular_price=regular_price, status=status,
                                                    image2=image2, image3=image3, image4=image4, image5=image5, video=video,
                                                    vip_price=vip_price, vvip_price=vvip_price, location=location,  description=description)
            
            sport_object.save();

            # create a general post
            post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Sport')
            post_object.save();

            messages.success(request, 'Submitted Successfully! Your Post will be reviewed before being displayed on your page and other pages.')
    
        return redirect('hostprofile')

@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def hostpostadventure(request):
    user = request.user
    profile = BookingHostProfile.objects.get(user=user)

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = profile.company_name
        title = request.POST.get('title')
        category = request.POST.get('category')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        time = request.POST.get('time')
        timeupto = request.POST.get('timeupto')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        video = request.FILES.get('video')
        status = 'Pending'

        
        
        if image == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            adventure_object = BookingAdventure.objects.create(user=user, unique_id=unique_id, title=title, organizer=organizer, upto=upto,
                                                    image=image, submitted_category=category,  date=date, time=time, timeupto=timeupto, contact_1=contact_1,
                                                    contact_2=contact_2, email=email, regular_price=regular_price, status=status,
                                                    image2=image2, image3=image3, image4=image4, image5=image5, video=video,
                                                    vip_price=vip_price, vvip_price=vvip_price, location=location,  description=description)
            
            adventure_object.save();

            # create a general post
            post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Adventure')
            post_object.save();

            messages.success(request, 'Submitted Successfully! Your Post will be reviewed before being displayed on your page and other pages.')
    
        return redirect('hostprofile')

@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def hostpostcar_rental(request):
    user = request.user
    profile = BookingHostProfile.objects.get(user=user)

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = profile.company_name
        name = request.POST.get('name')
        category = request.POST.get('category')
        engine_size = request.POST.get('engine_size')
        mileage = request.POST.get('mileage')
        year = request.POST.get('year')
        wheeldrive = request.POST.get('wheeldrive')
        transmission = request.POST.get('transmission')
        fuel_type = request.POST.get('fuel_type')
        no_of_doors = request.POST.get('no_of_doors')
        no_of_seats = request.POST.get('no_of_seats')
        exterior_color = request.POST.get('exterior_color')
        service_1 = request.POST.get('service_1')
        service_2 = request.POST.get('service_2')
        service_3 = request.POST.get('service_3')
        service_4 = request.POST.get('service_4')
        service_5 = request.POST.get('service_5')
        service_6 = request.POST.get('service_6')
        service_7 = request.POST.get('service_7') 
        service_8 = request.POST.get('service_8')
        nationality = request.POST.get('nationality')
        location = request.POST.get('location')
        vehicle_type_or_brand = request.POST.get('brand')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        video = request.FILES.get('video')
        status = 'Pending'

        
        
        if image == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            car_rental_object = BookingCarRental.objects.create(user=user, unique_id=unique_id, name=name, organizer=organizer, 
                                                    engine_size=engine_size, mileage=mileage, year=year, wheeldrive=wheeldrive, 
                                                    transmission=transmission, fuel_type=fuel_type, no_of_doors=no_of_doors, no_of_seats=no_of_seats,
                                                    exterior_color=exterior_color, service_1=service_1, service_2=service_2, service_3=service_3,
                                                    service_4=service_4, service_5=service_5, service_6=service_6, service_7=service_7, nationality=nationality,
                                                    service_8=service_8, image=image, submitted_category=category, vehicle_type_or_brand=vehicle_type_or_brand,   
                                                    contact_1=contact_1, contact_2=contact_2, email=email, price=price, status=status,
                                                    image2=image2, image3=image3, image4=image4, image5=image5, video=video,
                                                    location=location,  description=description)
            
            car_rental_object.save();

            # create a general post
            post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Car Rental')
            post_object.save();

            messages.success(request, 'Submitted Successfully! Your Post will be reviewed before being displayed on your page and other pages.')
    
        return redirect('hostprofile')

@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def hostpostarenobnb(request):
    user = request.user
    profile = BookingHostProfile.objects.get(user=user)

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = profile.company_name
        name = request.POST.get('name')
        category = request.POST.get('category')
        #obtain the id of that foreign key item from property feature and save it
        feature_id = request.POST.get('feature')
        new_feature = get_object_or_404(BookingArenoBnbPropertyFeature, id = feature_id )

        location = request.POST.get('location')
        nationality = request.POST.get('nationality')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        video = request.FILES.get('video')
        status = 'Pending'

        
        
        if image == None:
            messages.error(request, 'Please upload an image in the first image input box!')
        else: 
            arenobnb_object = BookingArenoBnb.objects.create(user=user, unique_id=unique_id, name=name, organizer=organizer, property_feature=new_feature,
                                                    image=image, submitted_category=category,  contact_1=contact_1, nationality=nationality,
                                                    contact_2=contact_2, email=email, price=price, status=status,
                                                    image2=image2, image3=image3, image4=image4, image5=image5, video=video,
                                                     location=location,  description=description)
            
            arenobnb_object.save();

            # create a general post
            post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Areno BNB')
            post_object.save();

            messages.success(request, 'Submitted Successfully! Your Post will be reviewed before being displayed on your page and other pages.')
    
        return redirect('hostprofile')


@only_host
@disabled_accounts
@restrict_admin
@login_required(login_url='login')
def delete_hostprofileimage(request): 
    if request.method == 'POST':
        # Delete user account
        user = request.user
        profile = get_object_or_404(BookingHostProfile, user=user)
        profile.profileimage.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('hostprofile') 














# forgot password
    
def emailconfirmation(request):
    arenodetails = ArenoContact.objects.all().first()
    if request.method == 'POST':
        email = request.POST.get('email')
        # Check if the email exists in CustomerProfile
        user = User.objects.filter(email=email).first()
        if CustomerProfile.objects.filter(user=user).exists():
            profile = get_object_or_404(CustomerProfile, user=user)
             # Generate token and save to profile
            token = str(uuid.uuid4())
            profile.passwordtoken = token
            profile.save()
            messages.success(request, "A reset link has been sent to your email and phone number!.")

            #send verification code for customer
            userfullname = profile.fullname
            userphonenumber = profile.phonenumber
            useremail = profile.email
            emailConfirmationPasswordCustomer(userfullname, userphonenumber, useremail, token)

        elif user:
            # If not found in CustomerProfile, check SellerProfile
            profile = get_object_or_404(SellerProfile, user=user)
            # Generate token and save to profile
            token = str(uuid.uuid4())
            profile.passwordtoken = token
            profile.save()
            messages.success(request, "A reset link has been sent to your email and phone number!.")

            #sending sms via beem
            #send verification code for seller
            userfullname = profile.fullname
            userphonenumber = profile.phonenumber
            useremail = profile.email
            emailConfirmationPasswordSeller(userfullname, userphonenumber, useremail, token)

        else:
            messages.warning(request, "User does not exist, Please try again!.")
            return render(request, 'login.html')
    
            
    context = {'arenodetails':arenodetails}
    return render(request, 'login.html', context)

def setnewpassword(request, passwordtoken):
    arenodetails = ArenoContact.objects.all().first()
    if request.method == 'POST':
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')
        
        try:
            # Try to find the password token in CustomerProfile
            profile = CustomerProfile.objects.get(passwordtoken=passwordtoken)
            token_valid = True
        except CustomerProfile.DoesNotExist:
            try:
                # If not found in CustomerProfile, try finding in SellerProfile
                profile = SellerProfile.objects.get(passwordtoken=passwordtoken)
                token_valid = True
            except SellerProfile.DoesNotExist:
                try:
                    # If not found in seller Profile, try finding in Host Profile
                    profile = BookingHostProfile.objects.get(passwordtoken=passwordtoken)
                    token_valid = True
                except BookingHostProfile.DoesNotExist:
                    token_valid = False
                    return redirect('login')

        if token_valid:
            # Validate the passwords
            if new_password != confirm_password:
                messages.info(request, "Passwords Do not match!")
                return redirect('setnewpassword', passwordtoken=passwordtoken)
            else:
                # Set the new hashed password for the user
                profile.user.set_password(new_password)
                update_session_auth_hash(request, profile.user)
                profile.user.save()
                
                # Clear the token in the user profile
                profile.passwordtoken = None
                profile.save()

                #sending success sms and email
                phonenumber = profile.phonenumber
                useremail = profile.email
                resetPasswordSuccess(phonenumber, useremail)
                    
                return redirect('login') 

    
    
    
    context = {'arenodetails':arenodetails}
    return render(request, 'setnewpassword.html', context)

def confirmemail(request, username):
    profile = get_object_or_404(CustomerProfile, email=username)
    
    if request.method == 'POST':
        token = request.POST.get('token')
        if token == profile.usertoken:
            profile.emailverified = 'Verified'
            profile.usertoken = ''
            profile.save()

            #sending success email and sms
            fullname = profile.fullname
            phonenumber = profile.phonenumber
            useremail = profile.email
            verifyEmail(fullname, phonenumber, useremail)
            
            messages.success(request, 'Your Email is Verified Successfuly! Log in to your account.')

        else:
            messages.error(request, 'Wrong Verification Numbers! please try Again')
            return render(request, 'confirmemail.html', {'profile': profile})
    
        
    context = {'profile':profile}
    return render(request, 'confirmemail.html', context)












# Admin dashboard views
def is_staff(user):
    return user.is_staff

def alertbadge():
    # admin alert badge icon display
    newuserforms = SellerRegistrationForm.objects.filter(status=None)
    newhostforms = BookingHostForm.objects.filter(status=None)
    newrestaurantforms = SellerRegistrationForm.objects.filter(businesstype='Restaurant', status=None)
    newshopforms = SellerRegistrationForm.objects.filter(businesstype='Shopping', status=None)
    newuserproducts = ShopProduct.objects.filter(action="Pending")
    newuserfoods = RestaurantFoodItem.objects.filter(action="Pending")
    newuserbookingposts = list(chain(
                                BookingEvent.objects.filter(status='Pending'),
                                BookingSports.objects.filter(status='Pending'),
                                BookingAdventure.objects.filter(status='Pending'),
                                BookingCarRental.objects.filter(status='Pending'),
                                BookingArenoBnb.objects.filter(status='Pending')
                            ))
    newbnbrequests = BookingRequest.objects.filter(status='Pending')
    newcarrequests = BookingCarRequest.objects.filter(status='Pending')
    newquestions = BookingQuestion.objects.filter(responce_status = 'Pending') 
    newusermessages = ArenoMessage.objects.filter(replied='Pending')

    return {
        'newuserforms': newuserforms,
        'newhostforms':newhostforms,
        'newrestaurantforms':newrestaurantforms,
        'newshopforms':newshopforms,
        'newuserproducts': newuserproducts,
        'newuserfoods': newuserfoods,
        'newuserbookingposts': newuserbookingposts,
        'newbnbrequests': newbnbrequests,
        'newcarrequests': newcarrequests,
        'newquestions': newquestions,
        'newusermessages': newusermessages,
    }


@staff_required
def admin(request):
    approvedsellers = SellerRegistrationForm.objects.filter(status='Approved')
    approvedsellers_count = approvedsellers.count()
    customers = CustomerProfile.objects.all()
    customerscount = customers.count()
    hosts = BookingHostProfile.objects.all()
    hostscount = hosts.count()

    query = request.GET.get('query', '').strip()
    if query:
        approvedsellers = approvedsellers.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    
    alert_data = alertbadge()


    context = {'approvedsellers':approvedsellers, 'approvedsellers_count':approvedsellers_count, 'customerscount':customerscount, 'hostscount':hostscount,
                'newuserforms': alert_data['newuserforms'],
                'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'],
                'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'],
                'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'],
                'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'],
                'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'], }
    return render(request, 'admin.html', context)

@staff_required
def adminuserdetails(request, pk=None):
    try:
        sellerform = SellerRegistrationForm.objects.get(pk=pk)
        message = sendMessagetoUser.objects.filter(email = sellerform.email).last()
    except SellerRegistrationForm.DoesNotExist:
        sellerform = None
        message = None

    alert_data = alertbadge()
    
   

    context = {'sellerform':sellerform, 'message':message,
            'newuserforms': alert_data['newuserforms'],
                'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'],
                'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'],
                'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'],
                'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'],
                'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminuserdetails.html', context)

@staff_required
def registerseller(request, pk=None):
    sellerform = SellerRegistrationForm.objects.get(pk=pk)

    if request.method == 'POST':
        username = request.POST.get('email')
        fullname = request.POST.get('fullname')
        businessname = request.POST.get('businessname')
        phonenumber = request.POST.get('phonenumber')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        website = request.POST.get('website')
        address = request.POST.get('address')
        location = request.POST.get('location')
        businesstype = request.POST.get('businesstype')
        if_shoppingcategory = request.POST.get('if_shoppingcategory')
        if_restaurantcategory = request.POST.get('if_restaurantcategory')
        is_businessregistered = request.POST.get('is_businessregistered')
        aboutbusiness = request.POST.get('aboutbusiness')
        password = request.POST.get('otp')
        status = 'Approved'
 

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Email  already exists!')
            return redirect('adminuserdetails', pk=sellerform.pk)
        
        if User.objects.filter(sellerprofile__businessname=businessname).exists():
            messages.info(request, 'Business Name already exists!')
            return redirect('adminuserdetails', pk=sellerform.pk)
         
        # Create User object
        user = User.objects.create_user(username=username, password=password, email=email,
                                         first_name=fullname)


        Profile = SellerProfile(user=user, fullname=fullname, businessname=businessname,
                                 phonenumber=phonenumber, mobile=mobile,
                                email=email, website=website, address=address, location=location,
                                businesstype=businesstype, if_shoppingcategory=if_shoppingcategory,
                                if_restaurantcategory=if_restaurantcategory, is_businessregistered=is_businessregistered,
                                aboutbusiness=aboutbusiness, status=status)

        token = str(uuid.uuid4())
        Profile.passwordtoken = token
        Profile.save();
        sellerform.status = 'Approved'
        sellerform.save();
        
        messages.success(request, 'User Successfully Registered. An Email and Sms was sent to the user.')

        #save a notification to the seller
        try:
            notification_user = user
            title = 'Welcome to ARENO!'
            notification_type = 'New Register'
            content = f"Hi! {fullname}, Congratulations! You're officially registered! Prepare to thrive as you connect, supply, and grow your business within our trusted community. Let the journey begin! Enjoy every moment!"
            #save the notification
            notification_object = Notification.objects.create(user=notification_user, title=title, content=content, type=notification_type )
            notification_object.save();
        except:
            pass
        
        #send email with the link to create a new password
        useremail = email
        registerSellerSuccess(fullname, phonenumber, useremail, token)

    

    context = {'sellerform':sellerform}
    return render(request, 'adminuserdetails.html', context)

@staff_required
def sendUserMessage(request):
    if request.method == 'POST':
        formuser = request.POST.get('user')
        fullname = request.POST.get('fullname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        message = request.POST.get('message')

        msg_object = sendMessagetoUser.objects.create(user=formuser, fullname=fullname, phonenumber=phonenumber,
                                                        email=email, message=message)
        msg_object.save()
        sendmessage_user(fullname, phonenumber, email, message) # send message and email to user
        messages.success(request, 'Message sent successfully!')

        return redirect(request.META.get("HTTP_REFERER"))
        
@staff_required
def adminrestaurants(request):
    approvedrestaurants = SellerRegistrationForm.objects.filter(businesstype='Restaurant' , status='Approved')
    approvedrestaurants_count = approvedrestaurants.count()

    query = request.GET.get('query', '').strip()
    if query:
        approvedrestaurants = approvedrestaurants.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'approvedrestaurants':approvedrestaurants,
               'approvedrestaurants_count':approvedrestaurants_count,
               'newuserforms': alert_data['newuserforms'],
                'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'],
                'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'],
                'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'],
                'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'],
                'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminrestaurants.html', context)

@staff_required
def adminpendingrestaurants(request):
    pendingrestaurants = SellerRegistrationForm.objects.filter(businesstype='Restaurant' , status=None)
    pendingrestaurants_count = pendingrestaurants.count()

    query = request.GET.get('query', '').strip()
    if query:
        pendingrestaurants = pendingrestaurants.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'pendingrestaurants':pendingrestaurants, 
               'pendingrestaurants_count':pendingrestaurants_count,
               'newuserforms': alert_data['newuserforms'],
                'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'],
                'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'],
                'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'],
                'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'],
                'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminpendingrestaurants.html', context)

@staff_required
def admindeclinedrestaurants(request):
    declinedrestaurants = SellerRegistrationForm.objects.filter(businesstype='Restaurant' , status='Declined')
    declinedrestaurants_count = declinedrestaurants.count()

    query = request.GET.get('query', '').strip()
    if query:
        declinedrestaurants = declinedrestaurants.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'declinedrestaurants':declinedrestaurants, 
               'declinedrestaurants_count':declinedrestaurants_count,
               'newuserforms': alert_data['newuserforms'],
                'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'],
                'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'],
                'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'],
                'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'],
                'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admindeclinedrestaurants.html', context)

@staff_required
def adminfoodposts(request):
    newfoods = RestaurantFoodItem.objects.filter(action="Pending")
    newfoods_count = newfoods.count()

    sellerprofile = SellerProfile.objects.all()
    
    query = request.GET.get('query', '').strip()
    if query:
        newfoods = newfoods.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context={'newfoods':newfoods, 'newfoods_count':newfoods_count, 
             'sellerprofile':sellerprofile, 'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminfoodposts.html', context)

@staff_required
def adminapprovedfoods(request):
    approvedfoods = RestaurantFoodItem.objects.filter(action='Approved')
    approvedfoods_count = approvedfoods.count()

    sellerprofile = SellerProfile.objects.all()
    
    query = request.GET.get('query', '').strip()
    if query:
        approvedfoods = approvedfoods.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context={'approvedfoods':approvedfoods, 'approvedfoods_count':approvedfoods_count, 
             'sellerprofile':sellerprofile, 'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminapprovedfoods.html', context)

@staff_required
def admindeclinedfoods(request):
    declinedfoods = RestaurantFoodItem.objects.filter(action='Declined')
    declinedfoods_count = declinedfoods.count()

    sellerprofile = SellerProfile.objects.all()
    
    query = request.GET.get('query', '').strip()
    if query:
        declinedfoods = declinedfoods.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context={'declinedfoods':declinedfoods, 'declinedfoods_count':declinedfoods_count, 
             'sellerprofile':sellerprofile, 'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admindeclinedfoods.html', context)



@staff_required
def adminshopping(request):
    approvedshops = SellerRegistrationForm.objects.filter(businesstype='Shopping' , status='Approved')
    approvedshops_count = approvedshops.count()

    query = request.GET.get('query', '').strip()
    if query:
        approvedshops = approvedshops.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'approvedshops':approvedshops, 'approvedshops_count':approvedshops_count
               , 'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminshopping.html', context)

@staff_required
def adminpendingshops(request):
    pendingshops = SellerRegistrationForm.objects.filter(businesstype='Shopping' , status=None)
    pendingshops_count = pendingshops.count()

    query = request.GET.get('query', '').strip()
    if query:
        pendingshops = pendingshops.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'pendingshops':pendingshops, 'pendingshops_count':pendingshops_count
               , 'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminpendingshops.html', context)


@staff_required
def admindeclinedshops(request):
    declinedshops = SellerRegistrationForm.objects.filter(businesstype='Shopping' , status='Declined')
    declinedshops_count = declinedshops.count()

    query = request.GET.get('query', '').strip()
    if query:
        declinedshops = declinedshops.filter(Q(businessname__icontains=query) | Q(email__icontains=query) |
                                                                Q(businesstype__icontains=query) | Q(date__icontains=query) |
                                                                Q(phonenumber__icontains=query) | Q(location__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'declinedshops':declinedshops, 'declinedshops_count':declinedshops_count, 
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admindeclinedshops.html', context)

@staff_required
def adminproductposts(request):
    newproducts = ShopProduct.objects.filter(action="Pending")
    newproducts_count = newproducts.count()

    sellerprofile = SellerProfile.objects.all() # fetch all sellers
    
    query = request.GET.get('query', '').strip()
    if query:
        newproducts = newproducts.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context={'newproducts':newproducts, 'newproducts_count':newproducts_count, 'sellerprofile':sellerprofile,
             'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminproductposts.html', context)

@staff_required
def itemaction(request, pk=None):
    newproduct = get_object_or_404(ShopProduct, pk=pk)
    profile = get_object_or_404(SellerProfile, user=newproduct.user)
    generalpost = get_object_or_404(GeneralPost, Post_Id = newproduct.unique_id)
    
    if request.method == 'POST':
        newproduct.action = request.POST.get('action')
        generalpost.status = request.POST.get('action')
        newproduct.save();
        generalpost.save()

        if newproduct.action == 'Approved':
            #approve item post
            
            try:
                notification_user = newproduct.user
                title = 'Post Item Accepted!'
                notification_type = 'approved_product'
                content = f"{newproduct.productname}"
                price = f"{newproduct.productprice}"
                item_id = newproduct.id
                item_name = 'Shop Product'
                #save the notification
                notification_object = Notification.objects.create(user=notification_user, title=title, content=content, price=price, type=notification_type, item_id=item_id, item_name=item_name )
                notification_object.save();
            except:
                pass
        elif  newproduct.action == 'Declined':
            #sending sms via beem
            url = beem_url

            data = {
                "source_addr": beem_source_addr,
                "encoding": 0,
                "message": f"Hellow! {profile.fullname}, We are sorry to inform you that the product you submitted for review on {newproduct.date} has been declined. Product Name: {newproduct.productname}, Product Id: {newproduct.id}. ",
                "recipients": [
                    {
                        "recipient_id": 1,
                        "dest_addr": f"{profile.phonenumber}"
                    }
                ]
            }
            username = beem_username
            password = beem_password
            response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                print("SMS sent successfully!")
            else:
                print("SMS sending failed. Status code:", response.status_code)
                print("Response:", response.text)
            
            #email sending
            subject = 'Product Post Declined!'
            message = f"Hellow! {profile.fullname}, We are sorry to inform you that the product you submitted for review on {newproduct.date} has been declined. Product Name: {newproduct.productname}, Product Id: {newproduct.id}. "
            from_email = from_email_title
            recipient_list = [profile.email, ]

            try:
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.reply_to = [from_email,]
                # Send email
                email.send()
                print('Email sent successfully!')
            except Exception as e:
                print('An error occurred while sending the email: {}'.format(str(e)))

            #send notification
            try:
                notification_user = newproduct.user
                title = 'Post Item Declined!'
                notification_type = 'declined_product'
                content = f"{newproduct.productname}"
                price = f"{newproduct.productprice}"
                item_id = newproduct.id
                item_name = 'Shop Product'
                #save the notification
                notification_object = Notification.objects.create(user=notification_user, title=title, content=content, price=price, type=notification_type, item_id=item_id, item_name=item_name )
                notification_object.save();
            except:
                pass
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('adminproductposts')

@staff_required
def foodaction(request, pk=None):
    newfood = get_object_or_404(RestaurantFoodItem, pk=pk)
    profile = get_object_or_404(SellerProfile, user=newfood.user)
    generalpost = get_object_or_404(GeneralPost, Post_Id = newfood.unique_id)

    if request.method == 'POST':
        newfood.action = request.POST.get('action')
        generalpost.status = request.POST.get('action')
        newfood.save();
        generalpost.save();

        if newfood.action == 'Approved':
            try:
                notification_user = newfood.user
                title = 'Post Item Accepted!'
                notification_type = 'approved_food'
                content = f"{newfood.productname}"
                price = f"{newfood.productprice}"
                item_id = newfood.id
                item_name = 'Restaurant Item'
                #save the notification
                notification_object = Notification.objects.create(user=notification_user, title=title, content=content, price=price, type=notification_type, item_id=item_id, item_name=item_name )
                notification_object.save();
            except:
                pass

        elif  newfood.action == 'Declined':

             #sending sms via beem
            url = beem_url

            data = {
                "source_addr": beem_source_addr,
                "encoding": 0,
                "message": f"Hellow! {profile.fullname}, We are sorry to inform you that the product you submitted for review on {newfood.date} has been declined. Product Name: {newfood.productname}, Product Id: {newfood.id}. ",
                "recipients": [
                    {
                        "recipient_id": 1,
                        "dest_addr": f"{profile.phonenumber}"
                    }
                ]
            }
            username = beem_username
            password = beem_password
            response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                print("SMS sent successfully!")
            else:
                print("SMS sending failed. Status code:", response.status_code)
                print("Response:", response.text)
            
            #email sending
            subject = 'Food Item Post Declined!'
            message = f"Hellow! {profile.fullname}, We are sorry to inform you that the product you submitted for review on {newfood.date} has been declined. Product Name: {newfood.productname}, Product Id: {newfood.id}. "
            from_email = from_email_title
            recipient_list = [profile.email, ]

            try:
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.reply_to = [from_email,]
                # Send email
                email.send()
                print('Email sent successfully!')
            except Exception as e:
                print('An error occurred while sending the email: {}'.format(str(e)))

            try:
                notification_user = newfood.user
                title = 'Post Item Declined!'
                notification_type = 'declined_food'
                content = f"{newfood.productname}"
                price = f"{newfood.productprice}"
                item_id = newfood.id
                item_name = 'Restaurant Item'
                #save the notification
                notification_object = Notification.objects.create(user=notification_user, title=title, content=content, price=price, type=notification_type, item_id=item_id, item_name=item_name )
                notification_object.save();
            except:
                pass
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('adminproductposts')

@staff_required
def adminapprovedproducts(request):
    approvedproducts = ShopProduct.objects.filter(action='Approved')
    approvedproducts_count = approvedproducts.count()

    sellerprofile = SellerProfile.objects.all() # fetch all sellers

    query = request.GET.get('query', '').strip()
    if query:
        approvedproducts = approvedproducts.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'approvedproducts':approvedproducts, 'approvedproducts_count':approvedproducts_count, 'sellerprofile':sellerprofile,
             'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminapprovedproducts.html', context)

@staff_required
def admindeclinedproducts(request):
    declinedproducts = ShopProduct.objects.filter(action='Declined')
    declinedproducts_count = declinedproducts.count()

    sellerprofile = SellerProfile.objects.all()
    
    query = request.GET.get('query', '').strip()
    if query:
        declinedproducts = declinedproducts.filter(Q(productname__icontains=query) | Q(productdescription__icontains=query) |
                                                Q(productlocation__icontains=query) | Q(user__sellerprofile__businessname__icontains=query) |
                                                Q(productcategory__icontains=query) | Q(productprice__icontains=query)).distinct()

    # alert badge
    alert_data = alertbadge()

    context = {'declinedproducts':declinedproducts, 'declinedproducts_count':declinedproducts_count, 'sellerprofile':sellerprofile,
             'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admindeclinedproducts.html', context)



@staff_required
def adminallitems(request):
    approvedfoods = RestaurantFoodItem.objects.filter(action='Approved')
    approvedfoods_count = approvedfoods.count()
    approveditems = ShopProduct.objects.filter(action='Approved')
    approveditems_count = approveditems.count()
    total = approvedfoods_count + approveditems_count

    #products query
    productquery = request.GET.get('productquery', '').strip()
    if productquery:
        approveditems = approveditems.filter(Q(productname__icontains=productquery) | Q(productdescription__icontains=productquery) |
                                                Q(productlocation__icontains=productquery) | Q(user__sellerprofile__businessname__icontains=productquery) |
                                                Q(productcategory__icontains=productquery) | Q(productprice__icontains=productquery)).distinct()
        
        context = {'approvedfoods_count':approvedfoods_count, 'approveditems':approveditems, 'approveditems_count':approveditems_count, 'total':total}
        return render(request, 'adminallitems.html', context)

    #foodquery
    foodquery = request.GET.get('foodquery', '').strip()
    if foodquery:
        approvedfoods = approvedfoods.filter(Q(productname__icontains=foodquery) | Q(productdescription__icontains=foodquery) |
                                                        Q(productlocation__icontains=foodquery) | Q(user__sellerprofile__businessname__icontains=foodquery) |
                                                        Q(productcategory__icontains=foodquery) | Q(productprice__icontains=foodquery)).distinct()
        
        context = {'approvedfoods_count':approvedfoods_count, 'approvedfoods':approvedfoods, 'approveditems_count':approveditems_count, 'total':total}
        return render(request, 'adminallitems.html', context)

    # alert badge
    alert_data = alertbadge()
    
    context = {'approvedfoods':approvedfoods, 'approvedfoods_count':approvedfoods_count, 
               'approveditems':approveditems, 'approveditems_count':approveditems_count, 'total':total,
             'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminallitems.html', context)


@staff_required
def adminuserdecline(request, pk=None):
    sellerform = get_object_or_404(SellerRegistrationForm, pk=pk)
    if request.method == 'POST':
        sellerform.status = 'Declined'
        sellerform.save()
        messages.info(request, 'An Email  and Sms has been sent to the user!')

        #sending sms via beem
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{sellerform.firstname} {sellerform.lastname}, \n\nSorry to inform you that your Application has been Declined. Please contact us for more information!",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{sellerform.phonenumber}"
                }
            ]
        }

        username = beem_username
        password = beem_password

        response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            print("SMS sent successfully!")
        else:
            print("SMS sending failed. Status code:", response.status_code)
            print("Response:", response.text)

        #email sending
        subject = 'Application Status!'
        message = f"{sellerform.firstname} {sellerform.lastname}, \n\nSorry to inform you that your Application has been Declined. Please contact us for more information!"
        from_email = from_email_title
        recipient_list = [sellerform.email, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

        
        
    context = {'sellerform':sellerform}
    return render(request, 'adminuserdetails.html', context)

@staff_required
def adminallbooking(request):
    events = BookingEvent.objects.filter(status='Approved')
    sports = BookingSports.objects.filter(status='Approved')
    adventures = BookingAdventure.objects.filter(status='Approved')
    car_rentals = BookingCarRental.objects.filter(status='Approved')
    arenobnbs = BookingArenoBnb.objects.filter(status='Approved')
    counter = events.count() + sports.count() + adventures.count() + car_rentals.count() + arenobnbs.count()
    #pending counter
    pendingcounter = BookingEvent.objects.filter(status='Pending').count() + BookingSports.objects.filter(status='Pending').count() + BookingAdventure.objects.filter(status='Pending').count() + BookingCarRental.objects.filter(status='Pending').count() + BookingArenoBnb.objects.filter(status='Pending').count()
    #active counter
    activecounter = BookingEvent.objects.filter(status='Approved').count() + BookingSports.objects.filter(status='Approved').count() + BookingAdventure.objects.filter(status='Approved').count() + BookingCarRental.objects.filter(status='Approved').count() + BookingArenoBnb.objects.filter(status='Approved').count()
    #declined counter
    declinedcounter = BookingEvent.objects.filter(status='Declined').count() + BookingSports.objects.filter(status='Declined').count() + BookingAdventure.objects.filter(status='Declined').count() + BookingCarRental.objects.filter(status='Declined').count() + BookingArenoBnb.objects.filter(status='Declined').count()

    try:
        userprofile = BookingHostProfile.objects.all()
    except BookingHostProfile.DoesNotExist:
        userprofile = None
        pass

    query = request.GET.get('query')
    cat = request.GET.get('cat')

    if (query and cat == 'Event')  or (cat == 'Event'):
        events = BookingEvent.objects.filter((Q(title__icontains=query) | Q(location__icontains=query)  |
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Approved')) 

        sports = BookingSports.objects.none()
        adventures = BookingAdventure.objects.none()
        car_rentals = BookingCarRental.objects.none()
        arenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Sport') or (cat == 'Sport'):
        sports = BookingSports.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Approved'))
         
        events = BookingEvent.objects.none()
        adventures = BookingAdventure.objects.none()
        car_rentals = BookingCarRental.objects.none()
        arenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Adventure') or (cat == 'Adventure'):
        adventures = BookingAdventure.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Approved'))
         
        events = BookingEvent.objects.none()
        sports = BookingSports.objects.none()
        car_rentals = BookingCarRental.objects.none()
        arenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Car Rental') or (cat == 'Car Rental'):
        car_rentals = BookingCarRental.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Approved'))
         
        events = BookingEvent.objects.none()
        sports = BookingSports.objects.none()
        adventures = BookingAdventure.objects.none()
        arenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Areno BNB') or (cat == 'Areno BNB'):
        arenobnbs = BookingArenoBnb.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Approved'))
         
        events = BookingEvent.objects.none()
        sports = BookingSports.objects.none()
        adventures = BookingAdventure.objects.none()
        car_rentals = BookingCarRental.objects.none()

    else:
        events = BookingEvent.objects.filter(status='Approved')
        sports = BookingSports.objects.filter(status='Approved')
        adventures = BookingAdventure.objects.filter(status='Approved')
        car_rentals = BookingCarRental.objects.filter(status='Approved')
        arenobnbs = BookingArenoBnb.objects.filter(status='Approved')
        
    # alert badge
    alert_data = alertbadge()


    context = {'events':events, 'sports':sports, 'adventures':adventures, 'car_rentals':car_rentals, 
               'arenobnbs':arenobnbs, 'counter':counter, 'pendingcounter':pendingcounter, 
               'activecounter':activecounter, 'declinedcounter':declinedcounter, 'query':query, 'cat':cat,
               'userprofile':userprofile,
                'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'] }
    return render(request, 'adminallbooking.html', context)

@staff_required
def adminpendingbookingposts(request):
    #pending counter
    pendingcounter = BookingEvent.objects.filter(status='Pending').count() + BookingSports.objects.filter(status='Pending').count() + BookingAdventure.objects.filter(status='Pending').count() + BookingCarRental.objects.filter(status='Pending').count() + BookingArenoBnb.objects.filter(status='Pending').count()
    #active counter
    activecounter = BookingEvent.objects.filter(status='Approved').count() + BookingSports.objects.filter(status='Approved').count() + BookingAdventure.objects.filter(status='Approved').count() + BookingCarRental.objects.filter(status='Approved').count() + BookingArenoBnb.objects.filter(status='Approved').count()
    #declined counter
    declinedcounter = BookingEvent.objects.filter(status='Declined').count() + BookingSports.objects.filter(status='Declined').count() + BookingAdventure.objects.filter(status='Declined').count() + BookingCarRental.objects.filter(status='Declined').count() + BookingArenoBnb.objects.filter(status='Declined').count()

    pendingevents = BookingEvent.objects.filter(status='Pending')
    pendingsports = BookingSports.objects.filter(status='Pending')
    pendingadventures = BookingAdventure.objects.filter(status='Pending')
    pendingcar_rentals = BookingCarRental.objects.filter(status='Pending')
    pendingarenobnbs = BookingArenoBnb.objects.filter(status='Pending')

    query = request.GET.get('query')
    cat = request.GET.get('cat')

    if (query and cat == 'Event')  or (cat == 'Event'):
        pendingevents = BookingEvent.objects.filter((Q(title__icontains=query) | Q(location__icontains=query)  |
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Pending')) 

        pendingsports = BookingSports.objects.none()
        pendingadventures = BookingAdventure.objects.none()
        pendingcar_rentals = BookingCarRental.objects.none()
        pendingarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Sport') or (cat == 'Sport'):
        pendingsports = BookingSports.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Pending'))
         
        pendingevents = BookingEvent.objects.none()
        pendingadventures = BookingAdventure.objects.none()
        pendingcar_rentals = BookingCarRental.objects.none()
        pendingarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Adventure') or (cat == 'Adventure'):
        pendingadventures = BookingAdventure.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Pending'))
         
        pendingevents = BookingEvent.objects.none()
        pendingsports = BookingSports.objects.none()
        pendingcar_rentals = BookingCarRental.objects.none()
        pendingarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Car Rental') or (cat == 'Car Rental'):
        pendingcar_rentals = BookingCarRental.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Pending'))
         
        pendingevents = BookingEvent.objects.none()
        pendingsports = BookingSports.objects.none()
        pendingadventures = BookingAdventure.objects.none()
        pendingarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Areno BNB') or (cat == 'Areno BNB'):
        pendingarenobnbs = BookingArenoBnb.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Pending'))
         
        pendingevents = BookingEvent.objects.none()
        pendingsports = BookingSports.objects.none()
        pendingadventures = BookingAdventure.objects.none()
        pendingcar_rentals = BookingCarRental.objects.none()

    else:
        pendingevents = BookingEvent.objects.filter(status='Pending')
        pendingsports = BookingSports.objects.filter(status='Pending')
        pendingadventures = BookingAdventure.objects.filter(status='Pending')
        pendingcar_rentals = BookingCarRental.objects.filter(status='Pending')
        pendingarenobnbs = BookingArenoBnb.objects.filter(status='Pending')
       
    # alert badge
    alert_data = alertbadge()

    context = {'pendingcounter':pendingcounter, 'activecounter':activecounter, 'declinedcounter':declinedcounter,
               'pendingevents':pendingevents, 'pendingsports':pendingsports, 'pendingadventures':pendingadventures, 
               'pendingcar_rentals':pendingcar_rentals, 'pendingarenobnbs':pendingarenobnbs,  'query':query, 'cat':cat,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'] }
    return render(request, 'adminpendingbookingposts.html', context)

@staff_required
def admindeclinedbookingposts(request):
    #pending counter
    pendingcounter = BookingEvent.objects.filter(status='Pending').count() + BookingSports.objects.filter(status='Pending').count() + BookingAdventure.objects.filter(status='Pending').count() + BookingCarRental.objects.filter(status='Pending').count() + BookingArenoBnb.objects.filter(status='Pending').count()
    #active counter
    activecounter = BookingEvent.objects.filter(status='Approved').count() + BookingSports.objects.filter(status='Approved').count() + BookingAdventure.objects.filter(status='Approved').count() + BookingCarRental.objects.filter(status='Approved').count() + BookingArenoBnb.objects.filter(status='Approved').count()
    #declined counter
    declinedcounter = BookingEvent.objects.filter(status='Declined').count() + BookingSports.objects.filter(status='Declined').count() + BookingAdventure.objects.filter(status='Declined').count() + BookingCarRental.objects.filter(status='Declined').count() + BookingArenoBnb.objects.filter(status='Declined').count()

    declinedevents = BookingEvent.objects.filter(status='Declined')
    declinedsports = BookingSports.objects.filter(status='Declined')
    declinedadventures = BookingAdventure.objects.filter(status='Declined')
    declinedcar_rentals = BookingCarRental.objects.filter(status='Declined')
    declinedarenobnbs = BookingArenoBnb.objects.filter(status='Declined')

    query = request.GET.get('query')
    cat = request.GET.get('cat')

    if (query and cat == 'Event')  or (cat == 'Event'):
        declinedevents = BookingEvent.objects.filter((Q(title__icontains=query) | Q(location__icontains=query)  |
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Declined')) 

        declinedsports = BookingSports.objects.none()
        declinedadventures = BookingAdventure.objects.none()
        declinedcar_rentals = BookingCarRental.objects.none()
        declinedarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Sport') or (cat == 'Sport'):
        declinedsports = BookingSports.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Declined'))
         
        declinedevents = BookingEvent.objects.none()
        declinedadventures = BookingAdventure.objects.none()
        declinedcar_rentals = BookingCarRental.objects.none()
        declinedarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Adventure') or (cat == 'Adventure'):
        declinedadventures = BookingAdventure.objects.filter((Q(title__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Declined'))
         
        declinedevents = BookingEvent.objects.none()
        declinedsports = BookingSports.objects.none()
        declinedcar_rentals = BookingCarRental.objects.none()
        declinedarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Car Rental') or (cat == 'Car Rental'):
        declinedcar_rentals = BookingCarRental.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Declined'))
         
        declinedevents = BookingEvent.objects.none()
        declinedsports = BookingSports.objects.none()
        declinedadventures = BookingAdventure.objects.none()
        declinedarenobnbs = BookingArenoBnb.objects.none()

    elif (query and cat == 'Areno BNB') or (cat == 'Areno BNB'):
        declinedarenobnbs = BookingArenoBnb.objects.filter((Q(name__icontains=query) | Q(location__icontains=query) | 
                                                    Q(organizer__icontains=query)) & Q(type=cat) , Q(status='Declined'))
         
        declinedevents = BookingEvent.objects.none()
        declinedsports = BookingSports.objects.none()
        declinedadventures = BookingAdventure.objects.none()
        declinedcar_rentals = BookingCarRental.objects.none()

    else:
        declinedevents = BookingEvent.objects.filter(status='Declined')
        declinedsports = BookingSports.objects.filter(status='Declined')
        declinedadventures = BookingAdventure.objects.filter(status='Declined')
        declinedcar_rentals = BookingCarRental.objects.filter(status='Declined')
        declinedarenobnbs = BookingArenoBnb.objects.filter(status='Declined')
       
    # alert badge
    alert_data = alertbadge()

    context = {'pendingcounter':pendingcounter, 'activecounter':activecounter, 'declinedcounter':declinedcounter,
               'declinedevents':declinedevents, 'declinedsports':declinedsports, 'declinedadventures':declinedadventures, 
               'declinedcar_rentals':declinedcar_rentals, 'declinedarenobnbs':declinedarenobnbs,  'query':query, 'cat':cat,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']  }
    return render(request, 'admindeclinedbookingposts.html', context)

@staff_required
def adminbookingrequests(request):
    carrequests = BookingCarRequest.objects.filter(status='Pending') # for car rental
    bnbrequests = BookingRequest.objects.filter(status='Pending') # for areno bnb rental
    counter = carrequests.count() + bnbrequests.count()
    #declined counter
    completedcounter = BookingRequest.objects.filter(status='Completed').count() + BookingCarRequest.objects.filter(status='Completed').count()
   
    query = request.GET.get('query')
    cat = request.GET.get('cat')
    if (query and cat == 'Areno BNB') or (cat == 'Areno BNB'):
        bnbrequests = BookingRequest.objects.filter((Q(fullname__icontains=query) | Q(post_name__icontains=query) |
                                                    Q(email__icontains=query)) & Q(type=cat) , Q(status = 'Pending')) 

        carrequests = BookingCarRequest.objects.none()

    elif (query and cat == 'Car Rental') or (cat == 'Car Rental'):
        carrequests =  BookingCarRequest.objects.filter((Q(fullname__icontains=query) | Q(post_name__icontains=query) |
                                                    Q(email__icontains=query)) & Q(type=cat) , Q(status = 'Pending'))
         
        bnbrequests = BookingRequest.objects.none()
    else:
        carrequests = BookingCarRequest.objects.filter(status='Pending')
        bnbrequests = BookingRequest.objects.filter(status='Pending')

    # alert badge
    alert_data = alertbadge()

    context = {'carrequests':carrequests, 'bnbrequests':bnbrequests, 'counter':counter, 
               'completedcounter':completedcounter, 'query': query, 'cat': cat,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'] }
    return render(request, 'adminbookingrequests.html', context)

@staff_required
def admincompletedrequests(request):
    pendingcounter = BookingCarRequest.objects.filter(status='Pending').count() + BookingRequest.objects.filter(status='Pending') .count()
    carrequests = BookingCarRequest.objects.filter(status='Completed') # for car rental
    bnbrequests = BookingRequest.objects.filter(status='Completed') # for areno bnb rental
    counter = carrequests.count() + bnbrequests.count()

    query = request.GET.get('query')
    cat = request.GET.get('cat')
    if (query and cat == 'Areno BNB') or (cat == 'Areno BNB'):
        bnbrequests = BookingRequest.objects.filter((Q(fullname__icontains=query) | Q(post_name__icontains=query) |
                                                    Q(email__icontains=query)) & Q(type=cat)  , Q(status = 'Completed')) 

        carrequests = BookingCarRequest.objects.none()

    elif (query and cat == 'Car Rental') or (cat == 'Car Rental'):
        carrequests =  BookingCarRequest.objects.filter((Q(fullname__icontains=query) | Q(post_name__icontains=query) |
                                                    Q(email__icontains=query)) & Q(type=cat)  , Q(status = 'Completed'))
         
        bnbrequests = BookingRequest.objects.none()
    else:
        carrequests = BookingCarRequest.objects.filter(status='Completed')
        bnbrequests = BookingRequest.objects.filter(status='Completed')

    # alert badge
    alert_data = alertbadge()

    context = {'carrequests':carrequests, 'bnbrequests':bnbrequests, 'counter':counter, 'pendingcounter':pendingcounter,
                'query': query, 'cat': cat,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admincompletedrequests.html', context)

@staff_required
def car_rentalrequestmessage(request, pk=None):
    try:
        car_request = get_object_or_404(BookingCarRequest, pk = pk)
    except BookingCarRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        car_request.message = request.POST.get('message')

        car_request.save()
        bookingRequestmessage(car_request.fullname, car_request.phonenumber, car_request.email, car_request.message)
        messages.success(request, 'Message sent successfully!')
        return redirect ('adminbookingrequests')

@staff_required
def arenobnbrequestmessage(request, pk=None):
    try:
        arenobnb = get_object_or_404(BookingRequest, pk = pk)
    except BookingRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        arenobnb.message = request.POST.get('message')

        arenobnb.save()
        bookingRequestmessage(arenobnb.fullname, arenobnb.phonenumber, arenobnb.email, arenobnb.message)
        messages.success(request, 'Message sent successfully!')
        return redirect ('adminbookingrequests')

@staff_required
def car_rentalrequestaction(request, pk=None):
    try:
        car_request = get_object_or_404(BookingCarRequest, pk = pk)
    except BookingCarRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        car_request.status = request.POST.get('action')

        car_request.save()
        bookingRequestactionmessage(car_request.fullname, car_request.phonenumber, car_request.email, car_request.post_name)

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect ('adminbookingrequests')

@staff_required
def arenobnbrequestaction(request, pk=None):
    try:
        arenobnb = get_object_or_404(BookingRequest, pk = pk)
    except BookingRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        arenobnb.status = request.POST.get('action')

        arenobnb.save()
        bookingRequestactionmessage(arenobnb.fullname, arenobnb.phonenumber, arenobnb.email, arenobnb.post_name)

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect ('adminbookingrequests')

@staff_required
def deletecar_rentalrequest(request, pk=None):
    try:
        car_request = get_object_or_404(BookingCarRequest, pk = pk)
    except BookingCarRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        car_request.delete()
        return redirect ('adminbookingrequests')

@staff_required
def adminbookingquestions(request):
    questions = BookingQuestion.objects.filter(responce_status = 'Pending') 
    counter = questions.count()
    repliedquestions = BookingQuestion.objects.filter(responce_status = 'Replied') 
    repliedcounter =repliedquestions.count()

    query = request.GET.get('query')
    if query:
        questions = BookingQuestion.objects.filter(Q(fullname__icontains=query) | Q(booking_title__icontains=query) |
                                                    Q(email__icontains=query) | Q(post_category__icontains=query) |
                                                    Q(question__icontains=query), Q(responce_status = 'Pending')) 

    # alert badge
    alert_data = alertbadge()

    context = {'questions':questions, 'counter':counter, 'repliedcounter':repliedcounter, 'query':query,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'] }
    return render(request, 'adminbookingquestions.html', context)

@staff_required
def adminbookingrepliedquestions(request):
    questions = BookingQuestion.objects.filter(responce_status = 'Replied') 
    counter = questions.count()
    pendingquestions = BookingQuestion.objects.filter(responce_status = 'Pending') 
    pendingcounter = pendingquestions.count()

    query = request.GET.get('query')
    if query:
        questions = BookingQuestion.objects.filter(Q(fullname__icontains=query) | Q(booking_title__icontains=query) |
                                                    Q(email__icontains=query) | Q(post_category__icontains=query) |
                                                    Q(question__icontains=query), Q(responce_status = 'Replied')) 

    # alert badge
    alert_data = alertbadge()

    context = {'questions':questions, 'counter':counter, 'pendingcounter':pendingcounter, 'query':query,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages'] }
    return render(request, 'adminbookingrepliedquestions.html', context)

@staff_required
def questionreply(request, pk):
    try:
        question = BookingQuestion.objects.get(pk = pk) 
    except BookingQuestion.DoesNotExist:
        question = None
        return redirect('admin')
    
    if request.method == 'POST':
        question.responce = request.POST.get('responce')
        question.responce_status = 'Replied'

        question.save()
        bookingRequestmessage(question.fullname, question.phonenumber, question.email, question.responce) # send the responce to user
        messages.success(request, 'Message sent successfully!')
        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('adminbookingquestions') 

@staff_required
def deletequestion(request, pk):
    try:
        question = BookingQuestion.objects.get(pk = pk) 
    except BookingQuestion.DoesNotExist:
        question = None
        return redirect('admin')
    
    if request.method == 'POST':
        question.delete()
        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('adminbookingquestions') 


@staff_required
def deletearenobnbrequest(request, pk=None):
    try:
        arenobnb = get_object_or_404(BookingRequest, pk = pk)
    except BookingRequest.DoesNotExist:
        return redirect('admin')
        
    if request.method == 'POST':
        arenobnb.delete()
        return redirect ('adminbookingrequests')

@staff_required
def eventaction(request, pk=None):
    event = get_object_or_404(BookingEvent, pk=pk)
    try:
        generalpost = GeneralPost.objects.get(Post_Id = event.unique_id)
    except GeneralPost.DoesNotExist:
        generalpost = None
        pass 

    if request.method == 'POST':
        status = request.POST.get('action')

        event.status = status
        event.save()
        if generalpost:
            generalpost.status = status
            generalpost.save()
        #send alert
        if event.status == 'Approved':
            bookingactivitysuccess(event.organizer, event.contact_1, event.email, 'event', event.title)
        elif event.status == 'Declined':
            bookingactivityfailure(event.organizer, event.contact_1, event.email, 'event', event.title)
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin', pk=None) 

@staff_required
def sportaction(request, pk=None):
    sport = get_object_or_404(BookingSports, pk=pk)
    try:
        generalpost = GeneralPost.objects.get(Post_Id = sport.unique_id)
    except GeneralPost.DoesNotExist:
        generalpost = None
        pass 

    if request.method == 'POST':
        status = request.POST.get('action')

        sport.status = status
        sport.save()
        if generalpost:
            generalpost.status = status
            generalpost.save()
        #send alert
        if sport.status == 'Approved':
            bookingactivitysuccess(sport.organizer, sport.contact_1, sport.email, 'sport', sport.title)
        elif sport.status == 'Declined':
            bookingactivityfailure(sport.organizer, sport.contact_1, sport.email, 'sport', sport.title)
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin', pk=None) 

@staff_required
def adventureaction(request, pk=None):
    adventure = get_object_or_404(BookingAdventure, pk=pk)
    try:
        generalpost = GeneralPost.objects.get(Post_Id = adventure.unique_id)
    except GeneralPost.DoesNotExist:
        generalpost = None
        pass 

    if request.method == 'POST':
        status = request.POST.get('action')

        adventure.status = status
        adventure.save()
        if generalpost:
            generalpost.status = status
            generalpost.save()
        #send alert
        if adventure.status == 'Approved':
            bookingactivitysuccess(adventure.organizer, adventure.contact_1, adventure.email, 'adventure', adventure.title)
        elif adventure.status == 'Declined':
            bookingactivityfailure(adventure.organizer, adventure.contact_1, adventure.email, 'adventure', adventure.title)
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin', pk=None) 

@staff_required
def car_rentalaction(request, pk=None):
    car_rental = get_object_or_404(BookingCarRental, pk=pk)
    try:
        generalpost = GeneralPost.objects.get(Post_Id = car_rental.unique_id)
    except GeneralPost.DoesNotExist:
        generalpost = None
        pass

    if request.method == 'POST':
        status = request.POST.get('action')

        car_rental.status = status
        car_rental.save()
        if generalpost:
            generalpost.status = status
            generalpost.save()
        #send alert
        if car_rental.status == 'Approved':
            bookingactivitysuccess(car_rental.organizer, car_rental.contact_1, car_rental.email, 'Car rental', car_rental.name)
        elif car_rental.status == 'Declined':
            bookingactivityfailure(car_rental.organizer, car_rental.contact_1, car_rental.email, 'Car rental', car_rental.name)
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin', pk=None) 

@staff_required
def arenobnbaction(request, pk=None):
    arenobnb = get_object_or_404(BookingArenoBnb, pk=pk)
    try:
        generalpost = GeneralPost.objects.get(Post_Id = arenobnb.unique_id)
    except GeneralPost.DoesNotExist:
        generalpost = None
        pass

    if request.method == 'POST':
        status = request.POST.get('action')

        arenobnb.status = status
        arenobnb.save()
        if generalpost:
            generalpost.status = status
            generalpost.save()
        #send alert
        if arenobnb.status == 'Approved':
            bookingactivitysuccess(arenobnb.organizer, arenobnb.contact_1, arenobnb.email, 'Areno BNB', arenobnb.name)
        elif arenobnb.status == 'Declined':
            bookingactivityfailure(arenobnb.organizer, arenobnb.contact_1, arenobnb.email, 'Areno BNB', arenobnb.name)
        else:
            pass

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin', pk=None) 


@staff_required
def adminhosts(request):
    approvedhosts = BookingHostForm.objects.filter(status='Approved')
    approvedhosts_count = approvedhosts.count()
    pendinghosts = BookingHostForm.objects.filter(status=None)
    pendinghosts_count = pendinghosts.count()
    declinedhosts = BookingHostForm.objects.filter(status='Declined')
    declinedhosts_count = declinedhosts.count()
    
    

    query = request.GET.get('query')
    if query:
        approvedhosts = BookingHostForm.objects.filter(Q(fullname__icontains=query) | Q(company_name__icontains=query) |
                                                        Q(email__icontains=query) | Q(phonenumber__icontains=query) | 
                                                        Q(category__icontains=query) | Q(about__icontains=query), Q(status = 'Approved'))

    # alert badge
    alert_data = alertbadge()

    context = {'approvedhosts':approvedhosts, 'approvedhosts_count':approvedhosts_count, 'pendinghosts_count':pendinghosts_count, 
                'declinedhosts_count':declinedhosts_count,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminhosts.html', context)


@staff_required
def adminpendinghosts(request):
    pendinghosts = BookingHostForm.objects.filter(status=None)
    pendinghosts_count = pendinghosts.count()
    declinedhosts = BookingHostForm.objects.filter(status='Declined')
    declinedhosts_count = declinedhosts.count()
    approvedhosts = BookingHostForm.objects.filter(status='Approved')
    approvedhosts_count = approvedhosts.count()

    query = request.GET.get('query')
    if query:
        pendinghosts = BookingHostForm.objects.filter(Q(fullname__icontains=query) | Q(company_name__icontains=query) |
                                                        Q(email__icontains=query) | Q(phonenumber__icontains=query) | 
                                                        Q(category__icontains=query) | Q(about__icontains=query), Q(status = None))

    # alert badge
    alert_data = alertbadge()

    context = {'pendinghosts':pendinghosts, 'pendinghosts_count':pendinghosts_count, 
               'declinedhosts_count':declinedhosts_count, 'approvedhosts_count':approvedhosts_count,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminpendinghosts.html', context)

@staff_required
def admindeclinedhosts(request):
    declinedhosts = BookingHostForm.objects.filter(status='Declined')
    declinedhosts_count = declinedhosts.count()
    pendinghosts = BookingHostForm.objects.filter(status=None)
    pendinghosts_count = pendinghosts.count()
    approvedhosts = BookingHostForm.objects.filter(status='Approved')
    approvedhosts_count = approvedhosts.count()

    query = request.GET.get('query')
    if query:
        declinedhosts = BookingHostForm.objects.filter(Q(fullname__icontains=query) | Q(company_name__icontains=query) |
                                                        Q(email__icontains=query) | Q(phonenumber__icontains=query) | 
                                                        Q(category__icontains=query) | Q(about__icontains=query), Q(status = 'Declined'))

    # alert badge
    alert_data = alertbadge()

    context = {'declinedhosts':declinedhosts, 'declinedhosts_count':declinedhosts_count, 
                'pendinghosts_count':pendinghosts_count, 'approvedhosts_count':approvedhosts_count,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'admindeclinedhosts.html', context)

@staff_required
def adminhostdetails(request, pk=None):
    hostform = get_object_or_404(BookingHostForm, pk=pk)
   
   # alert badge
    alert_data = alertbadge()

    context = {'hostform':hostform,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminhostdetails.html', context)

@staff_required
def registerhost(request, pk=None):
    hostform = get_object_or_404(BookingHostForm, pk=pk)
    if request.method == 'POST':
        username = request.POST.get('email')
        fullname = request.POST.get('fullname')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        role = request.POST.get('role')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        website = request.POST.get('website')
        social_media = request.POST.get('socialmedia')
        category = request.POST.get('category')
        about = request.POST.get('about')
        password = request.POST.get('otp')
        status = 'Approved'
        access = 'Host'
 

        if User.objects.filter(username=email).exists():
            messages.info(request, 'Email  already exists!')
            return redirect('adminhostdetails', pk=pk)
        else:
            if BookingHostProfile.objects.filter(company_name=company_name).exists():
                messages.info(request, 'Company Name already exists!')
                return redirect('adminhostdetails', pk=pk)
            else:
                # Create User object
                user = User.objects.create_user(username=username, password=password, email=email,
                                                first_name=fullname)

                token = str(uuid.uuid4())
                Profile = BookingHostProfile.objects.create(user=user, fullname=fullname, company_name=company_name, head_office_location=location,
                                                            company_role=role, phonenumber=phonenumber, email=email, socialmedia=social_media,
                                                            website=website, category=category, about=about, status=status, access=access, passwordtoken=token)

                Profile.save();

                hostform = BookingHostForm.objects.get(email=email, category=category, company_name=company_name)
                hostform.status = 'Approved'
                hostform.save();
                
                messages.success(request, 'Host Successfully Registered. An Email and Sms was sent to the user.')

                
                #send email with the link to create a new password
                useremail = email
                registerHostSuccess(fullname, phonenumber, useremail, token)

    context = {'hostform':hostform}
    return render(request, 'adminhostdetails.html', context)

@staff_required
def adminhostdecline(request, pk=None):
    hostform = get_object_or_404(BookingHostForm, pk=pk)
    if request.method == 'POST':
        hostform.status = 'Declined'
        hostform.save()
        messages.info(request, 'An Email  and Sms has been sent to the user!')
        registerHostDecline(hostform.fullname, hostform.phonenumber, hostform.email)

    context = {'hostform':hostform}
    return render(request, 'adminhostdetails.html', context)

@staff_required
def delete_form(request, email):
    try:
        sellerform = SellerRegistrationForm.objects.get(email=email)
    except SellerRegistrationForm.DoesNotExist:
        sellerform = None
        pass

    try:
        hostform = BookingHostForm.objects.get(email=email)
    except BookingHostForm.DoesNotExist:
        hostform = None
        pass

    if request.method == 'POST':
        if sellerform:
            sellerform.delete()
            messages.success(request, f"{sellerform.businessname} Registration Form has been deleted successfully.")
            return redirect('admin') 
        
        if hostform:
            hostform.delete()
            messages.success(request, f"{hostform.company_name} Registration Form has been deleted successfully.")
            return redirect('adminhosts') 
      
        
# admin login
def adminlog(request):
    user = request.user

    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        
        user= auth.authenticate(username=username, password=password)
        #trying to get if customer is verified or not

        if user is not None:
            if user.is_staff:
                auth.login(request, user)
                return redirect('admin')  # Redirect to admin dashboard
            else:
                return redirect('unauthorized')  # Redirect if the user is not an admin
        else:
            messages.error(request, 'Wrong Credentials! Please try again.')
            return redirect('adminlog')
    return render(request, 'adminlog.html')
        


# post pages
@staff_required
def admineventpage(request, pk=None): 
    try:
        event = BookingEvent.objects.get(pk = pk)
         # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=event.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
    except:
        return redirect('admin')

    context = {'event':event, 'postprofile':postprofile}
    return render(request, 'admineventpage.html', context)

@staff_required
def adminsportpage(request, pk=None): 
    try:
        sport = BookingSports.objects.get(pk = pk) # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=sport.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
    except:
        return redirect('admin')

    context = {'sport':sport, 'postprofile':postprofile}
    return render(request, 'adminsportpage.html', context)

@staff_required
def adminadventurepage(request, pk=None): 
    try:
        adventure = BookingAdventure.objects.get(pk = pk) # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=adventure.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
    except:
        return redirect('admin')

    context = {'adventure':adventure, 'postprofile':postprofile}
    return render(request, 'adminadventurepage.html', context)

@staff_required
def admincar_rentalpage(request, pk=None): 
    try:
        car_rental = BookingCarRental.objects.get(pk = pk) # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=car_rental.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
    except:
        return redirect('admin')

    context = {'car_rental':car_rental, 'postprofile':postprofile}
    return render(request, 'admincar_rentalpage.html', context)

@staff_required
def adminarenobnbpage(request, pk=None): 
    try:
        arenobnb = BookingArenoBnb.objects.get(pk = pk) # obtain post user profile details
        try:
            postprofile = BookingHostProfile.objects.get(user=arenobnb.user)
        except BookingHostProfile.DoesNotExist:
            postprofile = None
            pass
    except:
        return redirect('admin')

    context = {'arenobnb':arenobnb, 'postprofile':postprofile}
    return render(request, 'adminarenobnbpage.html', context)

@staff_required
def adminproductpage(request, pk=None):
    try:
        shopproduct = ShopProduct.objects.get(pk=pk)
        productuser = SellerProfile.objects.get(user=shopproduct.user)
    except ShopProduct.DoesNotExist:
        shopproduct = None
        productuser = None
        return redirect('admin')
    
        
    context = {'shopproduct':shopproduct, 'productuser':productuser}
    return render(request, 'adminproductpage.html', context)

@staff_required
def adminfoodpage(request, pk=None):
    try:
        fooditem = RestaurantFoodItem.objects.get(pk=pk)
        productuser = SellerProfile.objects.get(user=fooditem.user)
    except RestaurantFoodItem.DoesNotExist:
        fooditem = None
        productuser = None
        return redirect('admin')
    
        
    context = {'fooditem':fooditem, 'productuser':productuser}
    return render(request, 'adminfoodpage.html', context)

@staff_required
def adminmessagepage(request):
    usermessages = ArenoMessage.objects.filter(replied='Pending')
    messagecounter = usermessages.count()

    query = request.GET.get('query')
    if query:
        usermessages = ArenoMessage.objects.filter(Q(fullname__icontains=query) | Q(email__icontains=query) |
                                                Q(message__icontains=query) | Q(phonenumber__icontains=query), Q(replied='Pending'))
    
    # alert badge
    alert_data = alertbadge()
        
    context = {'usermessages':usermessages, 'messagecounter':messagecounter,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminmessagepage.html', context)

@staff_required
def adminrepliedmessagepage(request):
    usermessages = ArenoMessage.objects.filter(replied='Replied')
    messagecounter = usermessages.count()
    pendingmessages = ArenoMessage.objects.filter(replied='Pending')
    pendingmessagecounter = pendingmessages.count()

    query = request.GET.get('query')
    if query:
        usermessages = ArenoMessage.objects.filter(Q(fullname__icontains=query) | Q(email__icontains=query) | Q(reply__icontains=query) |
                                                Q(message__icontains=query) | Q(phonenumber__icontains=query), Q(replied='Replied'))
    
    # alert badge
    alert_data = alertbadge()
        
    context = {'usermessages':usermessages, 'messagecounter':messagecounter, 'pendingmessagecounter':pendingmessagecounter,
               'newuserforms': alert_data['newuserforms'], 'newhostforms': alert_data['newhostforms'],
                'newrestaurantforms': alert_data['newrestaurantforms'], 'newshopforms': alert_data['newshopforms'],
                'newuserproducts': alert_data['newuserproducts'], 'newuserfoods': alert_data['newuserfoods'],
                'newuserbookingposts': alert_data['newuserbookingposts'], 'newbnbrequests': alert_data['newbnbrequests'],
                'newcarrequests': alert_data['newcarrequests'], 'newquestions': alert_data['newquestions'],
                'newusermessages': alert_data['newusermessages']}
    return render(request, 'adminrepliedmessagepage.html', context)

@staff_required
def adminmessagepagereply(request, pk):
    try:
        usermessage = ArenoMessage.objects.get(pk = pk)
    except ArenoMessage.DoesNotExist:
        usermessage = None
        return redirect('admin')

    if request.method == 'POST':
        usermessage.reply = request.POST.get('responce')
        usermessage.save()

        messages.success(request, 'Message sent successfully!')
        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin')

@staff_required
def deleteusermessage(request, pk):
    try:
        usermessage = ArenoMessage.objects.get(pk = pk)
    except ArenoMessage.DoesNotExist:
        usermessage = None
        return redirect('admin')

    if request.method == 'POST':
        usermessage.delete()

        redirect_url = request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('admin')

@staff_required
def adminmessagepagesend(request):
    if request.method == 'POST':
        usermessage = request.POST.get('responce')
        fullname = request.POST.get('fullname','')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')

        if phonenumber.startswith ('0') or not phonenumber[1:].isdigit():
            messages.error(request, 'Write your phone number correctly, eg: 255***')
            return redirect ('adminmessagepage')
        else:
            message_object = ArenoMessage.objects.create(fullname=fullname, phonenumber=phonenumber, reply=usermessage, email=email)
            message_object.save()
        
            messages.success(request, 'Message sent successfully!')
            return redirect ('adminmessagepage')
            
@staff_required
def eventform(request):
    arenodetails = ArenoContact.objects.all().first()

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = request.POST.get('fullname')
        title = request.POST.get('title')
        category = request.POST.get('eventcat')
        venue = request.POST.get('venue')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        time = request.POST.get('time')
        timeupto = request.POST.get('timeupto')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        status = 'Pending'

        if any(image is None for image in [image, image2, image3, image4]):
            messages.error(request, 'Please upload atleast one image!')
        else:
            if contact_1.startswith ('0') or not contact_1[1:].isdigit() :
                    messages.error(request, 'Write phone number correctly, eg: 255***')
            else:
                event = BookingEvent.objects.create(unique_id=unique_id, title=title, submitted_category=category, venue=venue, location=location, date=date,
                                                    upto=upto, time=time, timeupto=timeupto, contact_1=contact_1, contact_2=contact_2, organizer=organizer, email=email, regular_price=regular_price,
                                                    image2=image2, image3=image3, image4=image4, 
                                                    vip_price=vip_price, vvip_price=vvip_price, description=description, image=image, status=status)

                event.save();

                # create a general post
                post_object = GeneralPost.objects.create(user=request.user, Post_Id=unique_id, ItemName=title,
                                                        Location=location, Description=description, Type='Event')
                post_object.save();

                activityForm(organizer, contact_1, email, 'event', title)
                messages.success(request, f"Event Successfully Submitted for review, {organizer}  will be notified soon.")

    context = {'arenodetails':arenodetails,}
    return render(request, 'eventform.html', context)

@staff_required
def sportform(request):
    arenodetails = ArenoContact.objects.all().first()

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = request.POST.get('fullname')
        title = request.POST.get('title')
        category = request.POST.get('sportcat')
        venue = request.POST.get('venue')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        timeupto = request.POST.get('timeupto')
        time = request.POST.get('time')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        status = 'Pending'

        if image == None:
            messages.error(request, 'Please upload an atleast one image!')
        else:
            if contact_1.startswith ('0') or not contact_1[1:].isdigit() :
                    messages.error(request, 'Write phone number correctly, eg: 255***')
            else:
                sport = BookingSports.objects.create(unique_id=unique_id, title=title, submitted_category=category, venue_or_stadium=venue, location=location, date=date,
                                                    upto=upto, time=time, timeupto=timeupto, contact_1=contact_1, contact_2=contact_2, organizer=organizer, email=email, regular_price=regular_price,
                                                    image2=image2, image3=image3, image4=image4, 
                                                    vip_price=vip_price, vvip_price=vvip_price, description=description, image=image, status=status )

                sport.save();
                # create a general post
                post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Sport')
                post_object.save();

                activityForm(organizer, contact_1, email, 'sport', title)
                messages.success(request, f"Sport Successfully Submitted for review, {organizer}  will be notified soon.")

    context = {'arenodetails':arenodetails}
    return render(request, 'sportform.html', context)

@staff_required
def adventureform(request):
    arenodetails = ArenoContact.objects.all().first()

    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        organizer = request.POST.get('fullname')
        title = request.POST.get('title')
        category = request.POST.get('adventurecat')
        venue = request.POST.get('venue')
        location = request.POST.get('location')
        date = request.POST.get('date')
        upto = request.POST.get('upto')
        time = request.POST.get('time')
        timeupto = request.POST.get('timeupto')
        contact_1 = request.POST.get('contact1')
        contact_2 = request.POST.get('contact2')
        email = request.POST.get('email')
        regular_price = request.POST.get('regularprice')
        vip_price = request.POST.get('vipprice')
        vvip_price = request.POST.get('vvipprice') 
        description = request.POST.get('description')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        status = 'Pending'

        if image == None:
            messages.error(request, 'Please upload an atleast one image!')
        else:
            if contact_1.startswith ('0') or not contact_1[1:].isdigit() :
                    messages.error(request, 'Write phone number correctly, eg: 255***')
            else:
                adventure = BookingAdventure.objects.create(unique_id=unique_id, title=title, submitted_category=category, venue=venue, location=location, date=date,
                                                    upto=upto, time=time, timeupto=timeupto, contact_1=contact_1, contact_2=contact_2, organizer=organizer, email=email, regular_price=regular_price,
                                                    image2=image2, image3=image3, image4=image4,
                                                    vip_price=vip_price, vvip_price=vvip_price, description=description, image=image, status=status)

                adventure.save();

                # create a general post
                post_object = GeneralPost.objects.create(Post_Id=unique_id, Type='Adventure')
                post_object.save();

                activityForm(organizer, contact_1, email, 'adventure' ,title)
                messages.success(request, f"Adventure Successfully Submitted for review, {organizer}  will be notified soon.")

    context = {'arenodetails':arenodetails}
    return render(request, 'adventureform.html', context)
   











