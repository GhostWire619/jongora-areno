from .models import Notification, ShopProduct, Cart, AdminCustomerNotification, RestaurantFoodItem, AdminSellerNotification, PendingPayment, SellerProfile
from .reports import generalErrorReport


# more extra functions

# create notification
def create_notification(title, type, content, price, user):
    try:
        if user.is_authenticated:
            #save the notification
            notification_object = Notification.objects.create(user=user, title=title, content=content, price=price, type=type )
            notification_object.save();
    except Exception as e:
        generalErrorReport(e, 'create_notification', 'functions.py') # send error
        print(f"an error occured: {e}")
        pass

# notifications display
def notification_data(user):
    if not user.is_authenticated:
        return {
            'cartcount' : 0,
            'pending_counter' : 0,
            'profile': None,
            'notifications': None,
            'new_signups': None,
            'cart_adds': None,
            'pending_purchases': None,
            'pending_food_purchases': None,
            'approved_products': None,
            'approved_products_count': 0,
            'approved_foods': None,
            'approved_foods_count': 0,
            'declined_products': None,
            'declined_foods': None,
            'customer_notifications': None,
            'seller_notifications': None,
            'pending_counter': 0,
            'pending_food_counter': 0,
            'notificationcount': 0,
        }

    # Initialize variables
    cart_objects = Cart.objects.filter(user=user)
    cartcount = cart_objects.count()
    notifications = Notification.objects.filter(user=user)
    new_signups = notifications.filter(type='New Register').first()
    cart_adds = notifications.filter(type='Cart').last()
    pending_purchases = notifications.filter(type='pending_purchase').last()
    pending_food_purchases = notifications.filter(type='pending_purchase_food').last()
    approved_products = notifications.filter(type='approved_product').last()
    all_approved_products = ShopProduct.objects.filter(user=user, action='Approved')
    approved_products_count = all_approved_products.count()
    approved_foods = notifications.filter(type='approved_food').last()
    all_approved_foods = RestaurantFoodItem.objects.filter(user=user, action='Approved')
    approved_foods_count = all_approved_foods.count()
    declined_products = notifications.filter(type='declined_product').last()
    declined_foods = notifications.filter(type='declined_food').last()
    customer_notifications = AdminCustomerNotification.objects.last()
    seller_notifications = AdminSellerNotification.objects.last()

    pendingpaymentitems = PendingPayment.objects.filter(user=user, item_name='Shop Product')
    pending_counter = pendingpaymentitems.count()
    pendingpaymentfooditems = PendingPayment.objects.filter(user=user, item_name='Restaurant Item')
    pending_food_counter = pendingpaymentfooditems.count()

    customer_notifications_count = AdminCustomerNotification.objects.count()
    seller_notifications_count = AdminSellerNotification.objects.count()

    notificationcount = notifications.count()
    if customer_notifications_count > 0 or seller_notifications_count > 0:
        notificationcount += 1

    # Fetch seller profile
    profile = None
    try:
        profile = SellerProfile.objects.get(user=user)
    except SellerProfile.DoesNotExist:
        pass

    return {
        'cartcount' : cartcount,
        'pending_counter' : pending_counter,
        'profile': profile,
        'notifications': notifications,
        'new_signups': new_signups,
        'cart_adds': cart_adds,
        'pending_purchases': pending_purchases,
        'pending_food_purchases': pending_food_purchases,
        'approved_products': approved_products,
        'approved_products_count': approved_products_count,
        'approved_foods': approved_foods,
        'approved_foods_count': approved_foods_count,
        'declined_products': declined_products,
        'declined_foods': declined_foods,
        'customer_notifications': customer_notifications,
        'seller_notifications': seller_notifications,
        'pending_counter': pending_counter,
        'pending_food_counter': pending_food_counter,
        'notificationcount': notificationcount,
    }