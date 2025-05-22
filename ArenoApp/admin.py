from django.contrib import admin
from django.utils.html import format_html

from .models import SellerRegistrationForm, SellerProfile, ShopProduct, ShopCategory, Cart, ShopBrand, RestaurantFoodItem, RestaurantCategory, CustomerProfile, ArenoRating, ArenoContact, ArenoMessage, SendMessageToAll, ArenoAbout, ArenoRefundPolicy, ArenoPrivacyPolicy, PendingPayment, ArenoHomeAd, ArenoShoppingAd, ArenoRestaurantAd, Notification, AdminCustomerNotification, AdminSellerNotification, BookingMainPage
from .models import BookingHostForm, BookingHostProfile, ArenoBookingAd, BookingEvent, BookingSports, BookingSportsCategory, BookingEventsCategory, BookingAdventure, BookingAdventureCategory, Following, GeneralPost, BookingCarRental, BookingCarRentalCategory
from .models import BookingArenoBnbPropertyFeature, BookingArenoBnb, BookingArenoBnbCategory, BookingRequest, BookingQuestion, BookingCarRequest, sendMessagetoUser


# Register your models here.

@admin.register(SellerRegistrationForm)
class SellerRegistrationFormAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'businessname', 'businesstype', 'phonenumber', 'status') 
    search_fields = ('firstname', 'businessname', 'businesstype', 'phonenumber')
    readonly_fields = ('status', )

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'businessname', 'businesstype', 'is_verified', 'display_image') 
    search_fields = ('fullname', 'businessname', 'businesstype', 'email')
    readonly_fields = ('fullname', 'email', 'website', 'location', 'working_start_hour', 'working_end_hour', 'working_start_day', 'working_end_day', 'businesstype', 'status', 'user', 'emailverified')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 40px; max-width: 40px;" />', obj.profileimage.url) if obj.profileimage else '-'

    display_image.short_description = 'profileimage'

@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ('productname', 'productprice', 'action', 'date' , 'productstatus', 'display_image') 
    readonly_fields = ('action', 'productprice', 'productstatus','user', 'unique_id')
    search_fields = ('productname', 'productprice', 'action', 'productstatus')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.productimage.url) if obj.productimage else '-'

    display_image.short_description = 'productimage'

admin.site.register(ShopCategory)
admin.site.register(ShopBrand)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_id', 'item_name')
    search_fields = ('item_name', 'user')

@admin.register(RestaurantFoodItem)
class RestaurantFoodItemAdmin(admin.ModelAdmin):
    list_display = ('productname', 'productprice', 'action', 'date', 'productstatus', 'display_image') 
    readonly_fields = ('action', 'productprice', 'productstatus', 'user', 'unique_id')
    search_fields = ('productname', 'productprice', 'action', 'productstatus')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.productimage.url) if obj.productimage else '-'

    display_image.short_description = 'productimage'

admin.site.register(RestaurantCategory)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phonenumber', 'email', 'emailverified', 'date', 'display_image') 
    readonly_fields = ('fullname', 'email', 'address', 'location', 'access', 'user', 'emailverified', 'usertoken')
    search_fields = ('fullname', 'phonenumber', 'email', 'user', )
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.profileimage.url) if obj.profileimage else '-'

    display_image.short_description = 'profileimage'

@admin.register(ArenoRating)
class ArenoRatingAdmin(admin.ModelAdmin):
    search_fields = ('fullname', 'review', 'ratings')
    list_display = ('fullname', 'ratings', 'email') 

@admin.register(ArenoContact)
class ArenoContactAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(ArenoMessage)
class ArenoMessageAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phonenumber', 'email', 'replied')
    search_fields = ('fullname', 'phonenumber', 'email', 'replied')
    readonly_fields = ('message', 'replied' )

@admin.register(SendMessageToAll)
class SendMessageToAllAdmin(admin.ModelAdmin):
    list_display = ('message', 'date')
    search_fields = ('message', )
    readonly_fields = ('date', )


admin.site.register(ArenoAbout)
    
@admin.register(ArenoRefundPolicy)
class ArenoRefundPolicyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True 
    
@admin.register(ArenoPrivacyPolicy)
class ArenoPrivacyPolicyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

@admin.register(PendingPayment)
class PendingPaymentAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'quantity')
    
@admin.register(ArenoHomeAd)
class ArenoHomeAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image') 
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(ArenoShoppingAd)
class ArenoShoppingAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image') 
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(ArenoRestaurantAd)
class ArenoRestaurantAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image') 
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(ArenoBookingAd)
class ArenoBookingAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image') 
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
    # list_display = ('title', 'user', 'date', 'type')
    # search_fields = ('title', 'user', 'type')
    # readonly_fields = ('type', 'item_id', 'item_name', 'user')


@admin.register(AdminCustomerNotification)
class AdminCustomerNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(AdminSellerNotification)
class AdminSellerNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True


@admin.register(BookingMainPage)
class BookingMainPageAdmin(admin.ModelAdmin):
    list_display = ('title_english', )
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'category', 'display_image')
    search_fields = ('title', 'date', 'time', 'organizer', 'email')
    readonly_fields = ('type', 'submitted_category', 'status', 'unique_id', 'user', 'submitted_date')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(BookingSports)
class BookingSportsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'category', 'display_image')
    search_fields = ('title', 'date', 'time', 'organizer', 'email')
    readonly_fields = ('type', 'submitted_category', 'status', 'unique_id', 'user', 'submitted_date')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(BookingSportsCategory)
class BookingSportsCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('title', )
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(BookingEventsCategory)
class BookingEventsCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('title',)
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(BookingAdventure)
class BookingAdventureAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'category', 'display_image')
    search_fields = ('title', 'date', 'time', 'organizer', 'email')
    readonly_fields = ('type', 'submitted_category', 'status', 'unique_id', 'user', 'submitted_date')
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(BookingAdventureCategory)
class BookingAdventureCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('title', )
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

# @admin.register(Following)
# class FollowingAdmin(admin.ModelAdmin):
#     readonly_fields = ('user', 'following_user', 'following_user_id' )


@admin.register(GeneralPost)
class GeneralPostAdmin(admin.ModelAdmin):
    list_display = ( 'Type',)
    search_fields = ('Type',)
    readonly_fields = ('Post_Id', 'Type')

@admin.register(BookingHostForm)
class BookingHostFormAdmin(admin.ModelAdmin):
    list_display = ( 'company_name', 'email', 'phonenumber', 'category', 'status', 'date')
    search_fields = ('company_name', 'email', 'phonenumber', 'category')
    readonly_fields = ('email', 'category', 'status' )

@admin.register(BookingHostProfile)
class BookingHostProfileAdmin(admin.ModelAdmin):
    list_display = ( 'company_name', 'email', 'phonenumber', 'category', 'date', 'display_image')
    search_fields = ('company_name', 'email', 'phonenumber', 'category')
    readonly_fields = ('user', 'email', 'date', 'category', 'emailverified', 'access', 'status' )
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.profileimage.url) if obj.profileimage else '-'

    display_image.short_description = 'profileimage'
 
@admin.register(BookingCarRental)
class BookingCarRentalAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'email', 'contact_1', 'category', 'submitted_date', 'display_image')
    search_fields = ('name', 'email', 'contact_1', 'organizer', 'category')
    readonly_fields = ('submitted_date', 'user', 'status', 'type', 'unique_id' )
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(BookingCarRentalCategory)
class BookingCarRentalCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('title', )
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

@admin.register(BookingArenoBnbPropertyFeature)
class BookingArenoBnbPropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ( 'feature',)

@admin.register(BookingArenoBnb)
class BookingArenoBnbAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'email', 'contact_1', 'category', 'submitted_date', 'display_image')
    search_fields = ('name', 'email', 'contact_1', 'organizer', 'category')
    readonly_fields = ('submitted_date', 'submitted_category', 'user', 'status', 'type', 'unique_id' )
    def display_image(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url) if obj.image else '-'

    display_image.short_description = 'image'

@admin.register(BookingArenoBnbCategory)
class BookingArenoBnbCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('title', )
    def has_add_permission(self, request):
            if self.model.objects.exists():
                return False
            return True

""" @admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phonenumber', 'email', 'check_in_date', 'check_out_date')
    search_fields = ('fullname', 'phonenumber', 'email', 'check_in_date', 'check_out_date')
    readonly_fields = ('user', 'submitted_date', 'status', 'type', 'post_id', 'host') """

""" @admin.register(BookingQuestion)
class BookingQuestionAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phonenumber', 'email', 'booking_title', 'responce_status' )
    search_fields = ('fullname', 'phonenumber', 'email', 'booking_title')
    readonly_fields = ('user', 'submitted_date', 'post_id', 'post_category', 'host', 'responce_status') """

""" @admin.register(BookingCarRequest)
class BookingCarRequestAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phonenumber', 'email', 'date', 'submitted_date')
    search_fields = ('fullname', 'phonenumber', 'email')
    readonly_fields = ('user', 'submitted_date', 'status', 'type', 'message', 'post_id', 'host') """

""" @admin.register(sendMessagetoUser)
class sendMessagetoUserAdmin(admin.ModelAdmin):
     list_display = ('fullname', 'phonenumber', 'email')
     search_fields = ('fullname', 'phonenumber', 'email')
     readonly_fields = ('user',) """









