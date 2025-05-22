import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
import uuid

#beem API
import requests
from requests.auth import HTTPBasicAuth
from .keydetails import beem_url, beem_username, beem_password, beem_source_addr, from_email_title

#django email
from django.core.mail import send_mail
from django.core.mail import EmailMessage

#bug reports
from .reports import generalErrorReport, sellerVerificationError
#email sms 
from .sms_emails import sendEmailToAll, sendMessageReply, accountaction


# Create your models here.. 

class SellerProfile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    bio = CKEditor5Field(config_name='extends', max_length=600, null=True, blank=True)
    businessname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=False)
    website = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=False)
    location = models.CharField(max_length=100, null=True, blank=False)
    businesstype = models.CharField(max_length=100, null=True, blank=False)
    if_shoppingcategory = models.CharField(max_length=100, null=True, blank=True)
    if_restaurantcategory = models.CharField(max_length=100, null=True, blank=True)
    is_businessregistered = models.CharField(max_length=100, null=True, blank=True)
    aboutbusiness = models.TextField( max_length=1500, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    passwordtoken = models.CharField(null=True, blank=True, max_length=500)
    working_start_hour = models.CharField(null=True, blank=True, max_length=50)
    working_end_hour = models.CharField(null=True, blank=True, max_length=50)
    working_start_day = models.CharField(null=True, blank=True, max_length=50)
    working_end_day = models.CharField(null=True, blank=True, max_length=50)
    profileimage = models.ImageField(upload_to="profileimages/", blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True, null=True)
    emailverified = models.CharField(max_length=50, null=True, blank=True,  default='Verified')
    ACCOUNT_ACTION = [('Enabled', 'Enable'), ('Disabled', 'Disable')]
    account_action = models.CharField(max_length=50, null=True, blank=True,  choices=ACCOUNT_ACTION, default='Enabled')
    account_action_reason = models.TextField( max_length=1500, null=True, blank=True)

    def __str__(self):
        return self.fullname
    
    class Meta:
        verbose_name_plural = 'Areno Seller Profiles'
    
    #sending account action notification
    def save(self, *args, **kwargs):
        if self.account_action == 'Disabled':
            accountaction(self.fullname, self.phonenumber, self.email, self.account_action)
        return super(SellerProfile, self).save(*args, **kwargs)

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.profileimage
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    address = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    access = models.CharField(max_length=100, null=True, blank=True, default='Customer')
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    passwordtoken = models.CharField(null=True, blank=True, max_length=500)
    usertoken = models.CharField(null=True, blank=True, max_length=100)
    emailverified = models.CharField(null=True, blank=True, max_length=50)
    profileimage = models.ImageField(upload_to="profileimages/", blank=True, null=True)

    def __str__(self):
        return self.fullname
    
    class Meta:
        verbose_name_plural = 'Areno Customer Profiles'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.profileimage
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class SellerRegistrationForm(models.Model):
    firstname = models.CharField(max_length=100, null=True, blank=False)
    lastname = models.CharField(max_length=100, null=True, blank=False)
    businessname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=False)
    website = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    businesstype = models.CharField(max_length=100, null=True, blank=False)
    if_shoppingcategory = models.CharField(max_length=100, null=True, blank=True)
    if_restaurantcategory = models.CharField(max_length=100, null=True, blank=True)
    is_businessregistered = models.CharField(max_length=100, null=True, blank=True)
    aboutbusiness = models.TextField( max_length=1500, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    class Meta:
        verbose_name_plural = 'Areno Seller Reg Forms'


class ShopProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    unique_id = models.CharField(max_length=100, null=True, blank=True, editable=False)
    productname = models.CharField(max_length=100, null=True, blank=False)
    productprice = models.CharField(max_length=50, null=True, blank=False)
    productlocation = models.CharField(max_length=100, null=True, blank=True)
    productsize = models.CharField(max_length=50, null=True, blank=True)
    productweight = models.CharField(max_length=50, null=True, blank=True)
    productcolor = models.CharField(max_length=50, null=True, blank=True)
    productavailability = models.CharField(max_length=50, null=True, blank=True)
    productcategory = models.CharField(max_length=50, null=True, blank=True)
    productstatus = models.CharField(max_length=50, blank=False, null=True)
    productbrand = models.CharField(max_length=50, null=True, blank=True)
    productdescription = models.TextField( max_length=1000, null=True, blank=True)
    action = models.CharField(max_length=50, null=True, blank=True, default="Pending")
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    productimage = models.ImageField(upload_to="productimages/", blank=False, null=True)
    productimage2 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage3 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage4 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage5 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productvideo = models.FileField(upload_to="productvideos/", blank=True, null=True)

    def __str__(self):
        return self.productname
    
    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.productimage,
            self.productimage2,
            self.productimage3,
            self.productimage4,
            self.productimage5,
            self.productvideo,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class ShopCategory(models.Model):
    categoryname = models.CharField(max_length=100, null=True, blank=False)
    categoryimage = models.ImageField(upload_to="categoryimages/", blank=True, null=True)

    def __str__(self):
        return self.categoryname
    
    class Meta:
        verbose_name_plural = "Shop Categories" 

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.categoryimage
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class ShopBrand(models.Model):
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Shop Brands"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, swappable=False, editable=False)
    item_id = models.CharField(max_length=100, null=True, editable=False)
    item_name = models.CharField(max_length=100, null=True, editable=False)

    class Meta:
        verbose_name_plural = "Cart Items" 

class PendingPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, swappable=False, editable=False)
    item_id = models.CharField(max_length=100, null=True, editable=False)
    item_name = models.CharField(max_length=100, null=True, editable=False)
    quantity = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    class Meta:
        verbose_name_plural = "Pending payment"

 
class RestaurantFoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    unique_id = models.CharField(max_length=100, null=True, blank=True, editable=False)
    productname = models.CharField(max_length=100, null=True, blank=False)
    productprice = models.CharField(max_length=50, null=True, blank=False)
    productlocation = models.CharField(max_length=100, null=True, blank=True)
    productsize = models.CharField(max_length=50, null=True, blank=True)
    productweight = models.CharField(max_length=50, null=True, blank=True)
    productcolor = models.CharField(max_length=50, null=True, blank=True)
    productavailability = models.CharField(max_length=50, null=True, blank=True)
    productcategory = models.CharField(max_length=50, null=True, blank=True)
    productstatus = models.CharField(max_length=50, null=True, blank=False)
    productdescription = models.TextField(max_length=1000, null=True, blank=True)
    action = models.CharField(max_length=50, null=True, blank=True, default="Pending")
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    productimage = models.ImageField(upload_to="foodimages/", blank=False, null=True)
    productimage2 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage3 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage4 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productimage5 = models.ImageField(upload_to="productimages/", blank=True, null=True)
    productvideo = models.FileField(upload_to="foodvideos/", blank=True, null=True)

    def __str__(self):
        return self.productname
    
    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.productimage,
            self.productimage2,
            self.productimage3,
            self.productimage4,
            self.productimage5,
            self.productvideo,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class RestaurantCategory(models.Model):
    categoryname = models.CharField(max_length=100, null=True, blank=False)
    categoryimage = models.ImageField(upload_to="categoryimages/", blank=True, null=True)

    def __str__(self):
        return self.categoryname
    
    class Meta:
        verbose_name_plural = "Restaurant Categories" 

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.categoryimage
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class ArenoRating(models.Model):
    fullname = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    ratings = models.CharField(max_length=50, null=True, blank=True)
    review = models.TextField( max_length=1000, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.fullname

class ArenoContact(models.Model):
    Areno_footer_content = models.CharField(max_length=100, null=True, blank=True )
    phonenumber_1 = models.IntegerField(null=True, blank=True)
    phonenumber_2 = models.IntegerField(null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    home_shopping_image = models.ImageField(upload_to="appimages/", blank=False, null=True)
    home_restaurants_image = models.ImageField(upload_to="appimages/", blank=False, null=True)
    home_booking_image = models.ImageField(upload_to="appimages/", blank=False, null=True)
    home_logistics_image = models.ImageField(upload_to="appimages/", blank=False, null=True)
    facebook_link = models.CharField(max_length=50, null=True, blank=True)
    twitter_x_link = models.CharField(max_length=50, null=True, blank=True)
    instagram_link = models.CharField(max_length=50, null=True, blank=True)
    whatsapp_link = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Areno Main Details'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.home_shopping_image,
            self.home_restaurants_image,
            self.home_booking_image,
            self.home_logistics_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class ArenoMessage(models.Model):
    fullname = models.CharField(max_length=50, null=True, blank=False)
    email = models.CharField(max_length=50, null=True, blank=True)
    phonenumber = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(max_length=5000, null=True, blank=True)
    reply = models.TextField(max_length=5000, null=True, blank=True)
    replied = models.CharField(max_length=50, null=True, blank=True, default="Pending")
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.fullname
    
    class Meta:
        verbose_name_plural = 'Areno Messages'

    def save(self, *args, **kwargs):
        new_reply = self.reply
        fullname = self.fullname
        phonenumber = self.phonenumber
        email = self.email

        if new_reply != None:
            self.replied = 'Replied'
            #sending sms and email reply
            sendMessageReply(new_reply, phonenumber, email, fullname)
        else:
            pass

        return super().save(*args, **kwargs)

class sendMessagetoUser(models.Model):
    user = models.CharField(max_length=50, null=True, blank=True)
    fullname = models.CharField(max_length=50, null=True, blank=False)
    email = models.CharField(max_length=50, null=True, blank=True)
    phonenumber = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(max_length=5000, null=True, blank=True)

    def __str__(self):
        return self.fullname
    
    class Meta:
        verbose_name_plural = 'Areno User Messages'



class ArenoAbout(models.Model):
    title = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to="appimages/", blank=True, null=True)
    content = CKEditor5Field(config_name='extends', max_length=6000, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Areno About Details'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.image
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class ArenoRefundPolicy(models.Model):
    title = models.CharField(max_length=100, null=True)
    content = CKEditor5Field(config_name='extends', max_length=6000, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Areno Refund Policies'

class ArenoPrivacyPolicy(models.Model):
    title = models.CharField(max_length=100, null=True)
    content = CKEditor5Field(config_name='extends', max_length=6000, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Areno Privacy Policies'

class ArenoHomeAd(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True)
    image = models.ImageField(upload_to="advertimages/", blank=False, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Areno Ads Home'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.image
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class ArenoShoppingAd(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True)
    image = models.ImageField(upload_to="advertimages/", blank=False, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Areno Ads Shopping'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.image
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class ArenoRestaurantAd(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True)
    image = models.ImageField(upload_to="advertimages/", blank=False, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Areno Ads Restaurant'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.image
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, null=True, blank=False)
    content = models.TextField(max_length=1000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=False)
    date = models.DateField(null=True, blank=True, auto_now_add=True)
    item_id = models.CharField(max_length=100, null=True, blank=True)
    item_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title


class AdminCustomerNotification(models.Model):
    title = models.CharField(max_length=100, null=True, blank=False)
    content = models.TextField(max_length=1000, null=True, blank=True)
    title_swahili = models.CharField(max_length=100, null=True, blank=False)
    content_swahili = models.TextField(max_length=1000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Admin Customer Notifications'

class AdminSellerNotification(models.Model):
    title = models.CharField(max_length=100, null=True, blank=False)
    content = models.TextField(max_length=1000, null=True, blank=True)
    title_swahili = models.CharField(max_length=100, null=True, blank=False)
    content_swahili = models.TextField(max_length=1000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Admin Seller Notifications'

class SendMessageToAll(models.Model):
    subject = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(max_length=1000, null=True, blank=False)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.message
    class Meta:
        verbose_name_plural = 'Areno Messages to All'

    def save(self, *args, **kwargs):
        message = self.message
        subject = self.subject
        
        sendEmailToAll(message, subject)

        return super().save(*args, **kwargs)






#booking
class BookingHostForm(models.Model):
    fullname = models.CharField(max_length=100, null=True, blank=False)
    company_name = models.CharField(max_length=100, null=True, blank=False)
    head_office_location = models.CharField(max_length=100, null=True, blank=True)
    company_role = models.CharField(max_length=500, null=True, blank=True)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    socialmedia = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=False)
    about = models.TextField(max_length=1000, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    host_ID = models.FileField(upload_to="booking_host_files/", blank=True, null=True)
    licence = models.FileField(upload_to="booking_host_files/", blank=True, null=True)
    other_document = models.FileField(upload_to="booking_host_files/", blank=True, null=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name_plural = 'Areno Host Reg Forms'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.host_ID,
            self.licence,
            self.other_document,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingHostProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    company_name = models.CharField(max_length=100, null=True, blank=False)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    head_office_location = models.CharField(max_length=100, null=True, blank=True)
    company_role = models.CharField(max_length=500, null=True, blank=True)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    socialmedia = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=False)
    about = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)
    passwordtoken = models.CharField(null=True, blank=True, max_length=500)
    usertoken = models.CharField(null=True, blank=True, max_length=100)
    access = models.CharField(max_length=100, null=True, blank=True, default='Host')
    is_verified = models.BooleanField(default=True, blank=True, null=True)
    emailverified = models.CharField(max_length=50, null=True, blank=True,  default='Verified')
    profileimage = models.ImageField(upload_to="profileimages/", blank=True, null=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    ACCOUNT_ACTION = [('Enabled', 'Enable'), ('Disabled', 'Disable')]
    account_action = models.CharField(max_length=50, null=True, blank=True,  choices=ACCOUNT_ACTION, default='Enabled')
    account_action_reason = models.TextField( max_length=1500, null=True, blank=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name_plural = 'Areno Host Profiles'

    #sending account action notification
    def save(self, *args, **kwargs):
        if self.account_action == 'Disabled':
            accountaction(self.fullname, self.phonenumber, self.email, self.account_action)
        return super(BookingHostProfile, self).save(*args, **kwargs)
    
    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.profileimage
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class BookingMainPage(models.Model):
    title_english = models.CharField(max_length=100, null=True, blank=False)
    title_swahili = models.CharField(max_length=100, null=True)
    main_content_english = models.CharField(max_length=500, null=True)
    main_content_swahili = models.CharField(max_length=500, null=True)
    events_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    sports_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    car_rentals_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    areno_bnb_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    travel_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    adventure_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)


    def __str__(self):
        return self.title_english

    class Meta:
        verbose_name_plural = "Booking Main Page" 

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.events_image,
            self.sports_image,
            self.car_rentals_image,
            self.areno_bnb_image,
            self.travel_image,
            self.adventure_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class ArenoBookingAd(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True)
    image = models.ImageField(upload_to="advertimages/", blank=False, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Areno Ads Booking'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        image = self.image
        if image and image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)

class BookingEvent(models.Model):
    CATEGORY_CHOICES = [
        ('Conferences', 'Conferences'),
        ('Seminars', 'Seminars'),
        ('WorkShops', 'WorkShops'),
        ('Festivals and Concerts', 'Festivals and Concerts'),
        ('Praise and Worship', 'Praise and Worship'),
        ('Parties and Ceremonies', 'Parties and Ceremonies'),
        ('Other', 'Other'),
    ]

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=100, blank=False, null=True, choices=CATEGORY_CHOICES)
    submitted_category = models.CharField(max_length=100, blank=False, null=True)
    venue = models.CharField(max_length=100, blank=False, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    date = models.CharField(max_length=100, blank=False, null=True)
    upto = models.CharField(max_length=100, blank=True, null=True)
    time = models.CharField(max_length=100, blank=False, null=True)
    timeupto = models.CharField(max_length=100, blank=True, null=True)
    contact_1 = models.CharField(max_length=100, blank=False, null=True)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    regular_price = models.CharField(max_length=50, blank=False, null=True)
    vip_price = models.CharField(max_length=50, blank=True, null=True)
    vvip_price = models.CharField(max_length=50, blank=True, null=True)
    description = CKEditor5Field(config_name='extends', max_length=5000, blank=True, null=True)
    image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    image2 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image3 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image4 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image5 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    video = models.FileField(upload_to="bookingvideos/", blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True, default='Event')
    status = models.CharField(max_length=50, blank=True, null=True, default='Pending')
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Events'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.image,
            self.image2,
            self.image3,
            self.image4,
            self.image5,
            self.video,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

    #this is to save the submitted category by user to category choices
    def save(self, *args, **kwargs):
        try:
            if self.submitted_category != None:
                self.category = self.submitted_category
            if self.unique_id == None:
                unique_id = str(uuid.uuid4())
                self.unique_id = unique_id
        except Exception as e:
            print(e)
            error = f"{e}, Failed to update submitted category when user submitted category of event or unique id in booking event model"
            generalErrorReport(error, 513, 'models.py' )
        return super(BookingEvent, self).save(*args, **kwargs)

class BookingEventsCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, default="Booking Events Categories Images")
    conference_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    seminar_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    workshop_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    festival_concert_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    praise_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    party_ceremony_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Events Categories'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.conference_image,
            self.seminar_image,
            self.workshop_image,
            self.festival_concert_image,
            self.praise_image,
            self.party_ceremony_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingSports(models.Model):
    CATEGORY_CHOICES = [
        ('Football & Soccer', 'Football & Soccer'),
        ('Basket Ball', 'Basket Ball'),
        ('VolleyBall', 'VolleyBall'),
        ('Tennis', 'Tennis'),
        ('Swimming', 'Swimming'),
        ('Boxing', 'Boxing'),
        ('Other', 'Other'),
    ]

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=100, blank=False, null=True, choices=CATEGORY_CHOICES)
    submitted_category = models.CharField(max_length=100, blank=False, null=True)
    venue_or_stadium = models.CharField(max_length=100, blank=False, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    date = models.CharField(max_length=100, blank=False, null=True)
    upto = models.CharField(max_length=100, blank=True, null=True)
    time = models.CharField(max_length=100, blank=False, null=True)
    timeupto = models.CharField(max_length=100, blank=True, null=True)
    contact_1 = models.CharField(max_length=100, blank=False, null=True)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    regular_price = models.CharField(max_length=50, blank=False, null=True)
    vip_price = models.CharField(max_length=50, blank=True, null=True)
    vvip_price = models.CharField(max_length=50, blank=True, null=True)
    description = CKEditor5Field(config_name='extends', max_length=5000, blank=True, null=True)
    image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    image2 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image3 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image4 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image5 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    video = models.FileField(upload_to="bookingvideos/", blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True, default='Sport')
    status = models.CharField(max_length=50, blank=True, null=True, default='Pending')
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Sports'

    #this is to save the submitted category by user to category choices
    def save(self, *args, **kwargs):
        try:
            if self.submitted_category != None:
                self.category = self.submitted_category
            if self.unique_id == None:
                unique_id = str(uuid.uuid4())
                self.unique_id = unique_id
        except Exception as e:
            print(e)
            error = f"{e}, Failed to update submitted category when user submitted category of sport or unique id in booking sport model"
            generalErrorReport(error, 585, 'models.py' )
        return super(BookingSports, self).save(*args, **kwargs)

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.image,
            self.image2,
            self.image3,
            self.image4,
            self.image5,
            self.video,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingSportsCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, default="Booking Sports Categories Images")
    football_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    basketball_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    volleyball_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    tennis_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    swimming_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    boxing_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Sports Categories'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.football_image,
            self.basketball_image,
            self.volleyball_image,
            self.tennis_image,
            self.swimming_image,
            self.boxing_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingAdventure(models.Model):
    CATEGORY_CHOICES = [
        ('National Parks & Game reserves', 'National Parks & Game reserves'),
        ('Hiking & Climbing', 'Hiking & Climbing'),
        ('Historical', 'Historical'),
        ('City Tour', 'City Tour'),
        ('Beaches & Coastal', 'Beaches & Coastal'),
        ('Other', 'Other'),
    ]

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=100, blank=False, null=True, choices=CATEGORY_CHOICES)
    submitted_category = models.CharField(max_length=100, blank=False, null=True)
    venue = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    date = models.CharField(max_length=100, blank=False, null=True)
    upto = models.CharField(max_length=100, blank=True, null=True)
    time = models.CharField(max_length=100, blank=False, null=True)
    timeupto = models.CharField(max_length=100, blank=True, null=True)
    contact_1 = models.CharField(max_length=100, blank=False, null=True)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    regular_price = models.CharField(max_length=50, blank=False, null=True)
    vip_price = models.CharField(max_length=50, blank=True, null=True)
    vvip_price = models.CharField(max_length=50, blank=True, null=True)
    description = CKEditor5Field(config_name='extends', max_length=5000, blank=True, null=True)
    image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    image2 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image3 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image4 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image5 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    video = models.FileField(upload_to="bookingvideos/", blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True, default='Adventure')
    status = models.CharField(max_length=50, blank=True, null=True, default='Pending')
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Adventures'

    #this is to save the submitted category by user to category choices
    def save(self, *args, **kwargs):
        try:
            if self.submitted_category != None:
                self.category = self.submitted_category
            if self.unique_id == None:
                unique_id = str(uuid.uuid4())
                self.unique_id = unique_id
        except Exception as e:
            print(e)
            error = f"{e}, Failed to update submitted category when user submitted category of adventure or unique id in booking adventure model"
            generalErrorReport(error, 657, 'models.py' )
        return super(BookingAdventure, self).save(*args, **kwargs)

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.image,
            self.image2,
            self.image3,
            self.image4,
            self.image5,
            self.video,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingAdventureCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, default="Booking Adventure Categories Images")
    city_tours_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    national_parks_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    hiking_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    historical_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    beaches_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    other_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Adventure Categories'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.city_tours_image,
            self.national_parks_image,
            self.hiking_image,
            self.historical_image,
            self.beaches_image,
            self.other_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingCarRental(models.Model):
    CATEGORY_CHOICES = [
        ('Standard Car', 'Standard Car'),
        ('SUV & 4WD', 'SUV & 4WD'),
        ('Pick-Up Truck', 'Pick-Up Truck'),
        ('Luxury Car', 'Luxury Car'),
        ('Mini-Van', 'Mini-Van'),
        ('Safari Car', 'Safari Car'),
        ('Mini-Bus', 'Mini-Bus'),
        ('Other', 'Other'),
    ]
    AVAILABILITY = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('Will be Available soon', 'Will be Available soon'),
    ]
    WHEELDRIVE = [
        ('2-Wheel Drive', '2-Wheel Drive'),
        ('4-Wheel Drive', '4-Wheel Drive'),
        ('All-Wheel Drive', 'All-Wheel Drive'),
    ]
   
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=100, blank=False, null=True, choices=CATEGORY_CHOICES)
    submitted_category = models.CharField(max_length=100, blank=False, null=True)
    vehicle_type_or_brand = models.CharField(max_length=100, blank=False, null=True)
    engine_size = models.CharField(max_length=100, blank=True, null=True)
    mileage = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    wheeldrive = models.CharField(max_length=100, blank=True, null=True, choices=WHEELDRIVE)
    transmission = models.CharField(max_length=100, blank=True, null=True)
    fuel_type = models.CharField(max_length=100, blank=True, null=True)
    no_of_doors = models.CharField(max_length=100, blank=True, null=True)
    no_of_seats = models.CharField(max_length=100, blank=True, null=True)
    exterior_color = models.CharField(max_length=100, blank=True, null=True)
    service_1 = models.CharField(max_length=100, blank=True, null=True)
    service_2 = models.CharField(max_length=100, blank=True, null=True)
    service_3 = models.CharField(max_length=100, blank=True, null=True)
    service_4 = models.CharField(max_length=100, blank=True, null=True)
    service_5 = models.CharField(max_length=100, blank=True, null=True)
    service_6 = models.CharField(max_length=100, blank=True, null=True)
    service_7 = models.CharField(max_length=100, blank=True, null=True)
    service_8 = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    contact_1 = models.CharField(max_length=100, blank=False, null=True)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=50, blank=False, null=True)
    description = CKEditor5Field(config_name='extends', max_length=5000, blank=True, null=True)
    availability = models.CharField(max_length=50, null=True, blank=True, choices=AVAILABILITY, default="Available")
    image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    image2 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image3 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image4 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image5 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    video = models.FileField(upload_to="bookingvideos/", blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True, default='Car Rental')
    status = models.CharField(max_length=50, blank=True, null=True, default='Pending')
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Booking Car Rentals'

    #this is to save the submitted category by user to category choices
    def save(self, *args, **kwargs):
        try:
            if self.submitted_category != None:
                self.category = self.submitted_category
            if self.unique_id == None:
                unique_id = str(uuid.uuid4())
                self.unique_id = unique_id
        except Exception as e:
            print(e)
            error = f"{e}, Failed to update submitted category when user submitted category of car rental or unique id in booking car rental model"
            generalErrorReport(error, 727, 'models.py' )
        return super(BookingCarRental, self).save(*args, **kwargs)

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.image,
            self.image2,
            self.image3,
            self.image4,
            self.image5,
            self.video,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)


class BookingCarRentalCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, default="Booking Car Rental Categories Images")
    standard_cars_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    suv_4wd_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    pick_up_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    luxury_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    minivan_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    safari_car_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    minibus_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Car Rental Categories'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.standard_cars_image,
            self.suv_4wd_image,
            self.pick_up_image,
            self.luxury_image,
            self.minivan_image,
            self.safari_car_image,
            self.minibus_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingArenoBnbPropertyFeature(models.Model):
    feature = models.CharField(max_length=100, blank=False, null=True)

    def __str__(self):
        return self.feature

    class Meta:
        verbose_name_plural = 'Booking Areno Bnb Property Features'

class BookingArenoBnb(models.Model):
    CATEGORY_CHOICES = [
        ('Home', 'Home'),
        ('Appartment', 'Appartment'),
        ('Hotel', 'Hotel'),
        ('Lodge', 'Lodge'),
        ('Villa', 'Villa'),
        ('Other', 'Other'),
    ]
    AVAILABILITY = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('Will be Available soon', 'Will be Available soon'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=100, blank=False, null=True, choices=CATEGORY_CHOICES)
    submitted_category = models.CharField(max_length=100, blank=False, null=True)
    property_feature = models.ForeignKey(BookingArenoBnbPropertyFeature, on_delete=models.SET_NULL, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=False, null=True)
    contact_1 = models.CharField(max_length=100, blank=False, null=True)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=50, blank=False, null=True)
    description = CKEditor5Field(config_name='extends', max_length=5000, blank=True, null=True)
    availability = models.CharField(max_length=50, null=True, blank=True, choices=AVAILABILITY, default="Available")
    image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    image2 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image3 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image4 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    image5 = models.ImageField(upload_to="bookingimages/", blank=True, null=True)
    video = models.FileField(upload_to="bookingvideos/", blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True, default='Areno BNB')
    status = models.CharField(max_length=50, blank=True, null=True, default='Pending')
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Booking Areno BnB'

    #this is to save the submitted category by user to category choices
    def save(self, *args, **kwargs):
        try:
            if self.submitted_category != None:
                self.category = self.submitted_category
            if self.unique_id == None:
                unique_id = str(uuid.uuid4())
                self.unique_id = unique_id
        except Exception as e:
            print(e)
            error = f"{e}, Failed to update submitted category when user submitted category of areno bnb or unique id in booking arenobnb model"
            generalErrorReport(error, 835, 'models.py' )
        return super(BookingArenoBnb, self).save(*args, **kwargs)

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.image,
            self.image2,
            self.image3,
            self.image4,
            self.image5,
            self.video,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)

class BookingArenoBnbCategory(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, default="Booking Areno BNB Categories Images")
    home_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    appartment_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    hotel_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    lodge_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    villa_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)
    other_image = models.ImageField(upload_to="bookingimages/", blank=False, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Booking Areno BNB Categories'

    # deleting image file from os and database completely
    def delete(self, *args, **kwargs):
        # List of file fields to delete
        files_to_delete = [
            self.home_image,
            self.appartment_image,
            self.hotel_image,
            self.lodge_image,
            self.villa_image,
            self.other_image,
        ]

        for file_field in files_to_delete:
            if file_field and file_field.name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
                if os.path.isfile(file_path): 
                    os.remove(file_path)  

        super().delete(*args, **kwargs)


class BookingRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    check_in_date = models.CharField(max_length=100, null=True, blank=False)
    check_out_date = models.CharField(max_length=100, null=True, blank=False)
    message = models.TextField(max_length=4000, null=True, blank=True)
    host = models.CharField(max_length=100, null=True, blank=True)
    post_name = models.CharField(max_length=100, null=True, blank=True)
    post_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=False, default="Pending")
    type = models.CharField(max_length=100, null=True, blank=False, default="Areno BNB")
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.fullname
    class Meta:
        verbose_name_plural = 'Booking ArenoBNB Requests'

class BookingCarRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    date = models.CharField(max_length=100, null=True, blank=False)
    host = models.CharField(max_length=100, null=True, blank=True)
    post_name = models.CharField(max_length=100, null=True, blank=True)
    post_id = models.CharField(max_length=100, null=True, blank=True)
    description = CKEditor5Field(config_name='extends', max_length=1000, null=True, blank=False)
    message = models.TextField(max_length=4000, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=False, default="Pending")
    type = models.CharField(max_length=100, null=True, blank=False, default="Car Rental")
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.fullname
    class Meta:
        verbose_name_plural = 'Booking Car Rental Requests'

class BookingQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    fullname = models.CharField(max_length=100, null=True, blank=False)
    phonenumber = models.CharField(max_length=100, null=True, blank=False)
    email = models.CharField(max_length=100, null=True, blank=False)
    booking_title = models.CharField(max_length=100, null=True, blank=False)
    host = models.CharField(max_length=100, null=True, blank=True)
    post_category = models.CharField(max_length=100, null=True, blank=True)
    post_id = models.CharField(max_length=100, null=True, blank=True)
    question = CKEditor5Field(config_name='extends', max_length=1000, null=True, blank=False)
    responce = CKEditor5Field(config_name='extends', max_length=1000, null=True, blank=True)
    responce_status = models.CharField(max_length=100, null=True, blank=True, default="Pending")
    submitted_date = models.DateField(null=True, blank=True, auto_now_add=True , max_length=20)

    def __str__(self):
        return self.fullname
    class Meta:
        verbose_name_plural = 'Booking Questions'

class BookingFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_id = models.CharField(max_length=100, null=True)

class UserRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    selleruser = models.CharField(max_length=100, null=True)
    rate = models.IntegerField(blank=True, null=True)









class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    following_user = models.CharField(max_length=100, null=True, blank=False)
    following_user_id = models.CharField(max_length=100, null=True, blank=False)

    
class GeneralPost(models.Model):
    Post_Id = models.CharField(max_length=100, blank=False, null=True, editable=False)
    Type = models.CharField(max_length=50, blank=True, null=True, editable=False)

    class Meta:
        verbose_name_plural = "General Posts"

