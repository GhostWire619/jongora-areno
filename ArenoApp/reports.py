
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from .keydetails import beem_url, beem_username, beem_password, beem_source_addr, from_email_title

# importing models

bugreport_email = 'arenobugreports@gmail.com'

def sellerLoginError():
    subject = 'Seller Log In Error!'
    message = f"This error occured: Seller / Customer failed to log in to the account resulting in an error. (Login View)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def orderDetailsError(e):
    subject = 'Order Detail Error!'
    message = f"This error occured: {e}, User failed to see the order details of a product. (Order Detail View)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def foodOrderSummaryError(e):
    subject = 'Food Order summary Error!'
    message = f"This error occured: {e} , User failed to see the food order summary. (Food Order Summary View)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def pendingPaymentError(e):
    subject = 'Food Payment Error!'
    message = f"This error occured: {e} at (Restaurant Payment method View)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def sellerVerificationError(e):
    subject = 'Seller verification update Error!'
    message = f"This error occured: {e}. (seller profile: models.py)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def sendingMessageToAllError(e):
    subject = 'Sending message to all users Error!'
    message = f"This error occured: {e}, when admin tried to send sms message to all users. (send message to all: at sms_email.py)"
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))   

def generalErrorReport(error, view, pagename):
    subject = 'An Error occured!'
    message = f"This error occured: \n\nError: {error}. \nview name: {view} in {pagename} "
    from_email = from_email_title  
    recipient_list = [bugreport_email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [from_email,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e))) 











