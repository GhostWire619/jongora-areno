
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from .keydetails import beem_url, beem_username, beem_password, beem_source_addr, from_email_title, email_reply_to


#bug reports
from .reports import sendingMessageToAllError,  generalErrorReport

def sendEmailToAll(model_message, model_subject):
    from ArenoApp.models import SellerProfile, CustomerProfile

    users = User.objects.all()

    #getting all user emails and sending email to all
    for user in users:
        #send email to user
        subject = model_subject
        message = model_message
        useremail = user.email
        from_email = from_email_title  
        recipient_list = [useremail,]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

        #getting all user phone numbers basing on their profiles
        try:
            try:
                # getting phone number from sellers
                sellerprofile = SellerProfile.objects.get(user=user)
                if sellerprofile.phonenumber:
                    #send sms to user
                    phonenumber = sellerprofile.phonenumber
                    #sending sms via beem
                    url = beem_url
                    data = {
                        "source_addr": beem_source_addr,
                        "encoding": 0,
                        "message": model_message,
                        "recipients": [
                            {"recipient_id": 1,
                            "dest_addr": f"{phonenumber}" }]}
                    username = beem_username
                    password = beem_password
                    response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))
                    if response.status_code == 200:
                        print("SMS sent successfully!")
                    else:
                        print("SMS sending failed. Status code:", response.status_code)
                        print("Response:", response.text)

            except SellerProfile.DoesNotExist:
                # if user is not a seller, then check if he is a customer
                try:
                    customerprofile = CustomerProfile.objects.get(user=user)
                    if customerprofile.phonenumber:
                        #send sms to user
                        phonenumber = customerprofile.phonenumber
                        #sending sms via beem
                        url = beem_url
                        data = {
                            "source_addr": beem_source_addr,
                            "encoding": 0,
                            "message": model_message,
                            "recipients": [
                                {"recipient_id": 1,
                                "dest_addr": f"{phonenumber}" }]}
                        username = beem_username
                        password = beem_password
                        response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))
                        if response.status_code == 200:
                            print("SMS sent successfully!")
                        else:
                            print("SMS sending failed. Status code:", response.status_code)
                            print("Response:", response.text)
                except:
                    pass

            except Exception as e:
                print(f"This error occured: {e}")
                sendingMessageToAllError(e)


        except Exception as e:
            print(f"This error occured: {e}")
            error = f"This error occured: {e}"
            pagename = "sms_emails"
            generalErrorReport(error, 91, pagename)

def sellerForm(firstname, lastname, phonenumber, useremail):
    try:
        #sms
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"hi {firstname} {lastname}!, \n\nYour Application Form is Successfully Submitted for review, You will be notified soon. \n\nThank You! \nAreno Team.",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Application Form Submitted Successfully!'
        message = f"hi {firstname} {lastname}!, \n\nYour Application Form is Successfully Submitted for review, You will be notified soon. \n\nThank You! \nAreno Team."
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except Exception as e:
        print('failed to send email and message to user at register form ')
        sms_email = 'sms_email_view'
        generalErrorReport(e, 136, sms_email)

def logInCode(fullname, combined_number, useremail):
    #email sending email with the verification code
    subject = f"Email Verification Code: {combined_number}"
    message = f"Hi! {fullname}, \n\nHere is your email verification code. Please dont share this code with anyone. \n\nCode: {combined_number} \n\nThanks for choosing us! \nAreno Team."
    from_email = from_email_title
    recipient_list = [useremail, ]
    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.reply_to = [email_reply_to,]
        # Send email
        email.send()
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email: {}'.format(str(e)))

def contactAreno(fullname, phonenumber, useremail):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \nThank you for reaching out! Your message is important to us, and we appreciate you taking the time to connect with us. A member of our team will reach out to you shortly to assist you further. \n\nFor any concerns please reach out to us via, \nEmail: Support@areno.co.tz \n\nThank you again for contacting us. \nAreno Team.",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Thank you for reaching out to us!'
        message = f"Hi! {fullname}, \nThank you for reaching out! Your message is important to us, and we appreciate you taking the time to connect with us. A member of our team will reach out to you shortly to assist you further. \n\nFor any concerns please reach out to us via, \nEmail: Support@areno.co.tz \n\nThank you again for contacting us. \nAreno Team."
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        pass

def emailConfirmationPasswordCustomer(fullname, phonenumber, useremail, token):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \n\nFollow the link below to create your new password, Note that this link will only be used once! \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Create New Password!'
        message = f"Hi! {fullname}, \n\nFollow the link below to create your new password, Note that this link will only be used once! \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'failed to send verification code to create a password'
        pagename = 'sms_emails'
        generalErrorReport(error, 236, pagename)

def emailConfirmationPasswordSeller(fullname, phonenumber, useremail, token):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \n\nFollow the link below to create your new password, Note that this link will only be used once! \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Create New Password!'
        message = f"Hi! {fullname}, \n\nFollow the link below to create your new password, Note that this link will only be used once! \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'failed to send verification code to create a password'
        pagename = 'sms_emails'
        generalErrorReport(error, 236, pagename)

def resetPasswordSuccess(phonenumber, useremail):
    #sending sms
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Your password has been created successfully!, Login with your new password.",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'New Password Created!'
        message = f"Your password has been created successfully!, Login with your new password."
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'failed to send success email and sms for completing a reset password'
        pagename = 'sms_emails'
        generalErrorReport(error, 323, pagename)


def verifyEmail(fullname, phonenumber, useremail):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \n\nWelcome to ARENO! \nGet ready to dive into a world of shopping and discover the treasures our sellers have in store for you. \n\nEnjoy the experience! \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Welcome to ARENO!'
        message = f"Hi! {fullname}, \n\nYou are registration is completed! \nGet ready to shop with us and explore what our sellers have to offer. \n\nThank you for choosing us,  ENJOY! \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'failed to send success email and sms for verifyng email'
        pagename = 'sms_emails'
        generalErrorReport(error, 366, pagename)

def sendMessageReply(new_reply, phonenumber, useremail, fullname):
     #sending sms via beem
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{new_reply}",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Hi! {fullname},"
        message = f"{new_reply}"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send reply email and sms for users who sent a message to areno'
        pagename = 'sms_emails'
        generalErrorReport(error, 419, pagename)

def verificationUpdate(phonenumber, useremail, message):

    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{message}",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Congratulations!."
        message = f"{message}"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except:
        error = 'Failed to send verification update email and sms for users to be verified'
        pagename = 'sms_emails'
        generalErrorReport(error, 463, pagename)

def updatedPhonenumber(phonenumber, useremail):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Your phone number has been updated successfully!",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Success!"
        message = f"Your phone number has been updated successfully!"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except:
        error = 'Failed to send phonenumber update success email and sms for users'
        pagename = 'sms_emails'
        generalErrorReport(error, 465, pagename)

def registerSellerSuccess(fullname, phonenumber, useremail, token):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{fullname}, \nWelcome to ARENO! \nyour Application has been Accepted. Follow the link below to create a password to your account, \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Welcome to ARENO!'
        message = f"{fullname}, \nWelcome to ARENO! \nyour Application has been Accepted. Follow the link below to create a password to your account, \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send success email for a seller to create a new password'
        pagename = 'sms_emails'
        generalErrorReport(error, 508, pagename)

def activityForm(fullname, phonenumber, useremail, activity ,title):
    try:
        #sms
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{fullname}, \nYour {activity}: {title}, is Successfully Submitted for review, You will be notified soon. Thank You!",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Form Submitted Successfully!'
        message = f"Hello! {fullname}, Your {activity}: {title}, is Successfully Submitted for review, You will be notified soon. Thank You!"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except Exception as e:
        print('failed to send email and message to user at event form ')
        sms_email = 'sms_email_view'
        generalErrorReport(e, 555, sms_email)

def bookingactivitysuccess(fullname, phonenumber, useremail, activity, title):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \nYour {activity}: {title}, approval has been successful! For further information or any concerns, please contact us.",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Success!"
        message = f"Hi! {fullname}, Your {activity}: {title}, approval has been successful! For further information or any concerns, please contact us"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except:
        error = 'Failed to send phonenumber update success email and sms for users'
        pagename = 'sms_emails'
        generalErrorReport(error, 600, pagename)

def bookingactivityfailure(fullname, phonenumber, useremail, activity, title):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \nWe are sorry to inform you that Your {activity}: {title}, approval has been declined! For further information or any concerns, please contact us, \n\nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Unsuccessful!"
        message = f"Hi! {fullname}, \nWe are sorry to inform you that Your {activity}: {title}, approval has been declined! For further information or any concerns, please contact us, \n\nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except:
        error = 'Failed to send phonenumber update success email and sms for users'
        pagename = 'sms_emails'
        generalErrorReport(error, 644, pagename)

def accountaction(fullname, phonenumber, useremail, action):
    try:
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hello! {fullname}, \n\nYour account has been {action}! For further information or any concerns, please contact us, \n\nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Account Action!"
        message = f"Hello! {fullname}, \n\nYour account has been {action}! For further information or any concerns, please contact us, \n\nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except:
        error = 'Failed to send phonenumber update success email and sms for users'
        pagename = 'sms_emails'
        generalErrorReport(error, 686, pagename)

def HostForm(fullname, company_name, phonenumber, useremail):
    try:
        #sms
        url = beem_url
        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{fullname}, \nYour Application Form for {company_name} is Successfully Submitted for review, You will be notified soon. \n\nThank You! \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Host Application Form Submitted Successfully!'
        message = f"{fullname}, \nYour Application Form for {company_name} is Successfully Submitted for review, You will be notified soon. \n\nThank You! \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))

    except Exception as e:
        print('failed to send email and message to user at host register form')
        sms_email = 'sms_email_view'
        generalErrorReport(e, 729, sms_email)

def registerHostSuccess(fullname, phonenumber, useremail, token):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{fullname}, \nWelcome to ARENO! your Application has been Accepted. Follow the link below to create a password to your account, \n\nhttps://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Welcome to ARENO!'
        message = f"{fullname}, \nWelcome to ARENO! your Application has been Accepted. Follow the link below to create a password to your account, https://areno.co.tz/setnewpassword/{token} \n\n\nFor any complications please reach out to us via, \nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [email_reply_to,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send success email for a host to create a new password'
        pagename = 'sms_emails'
        generalErrorReport(error, 774, pagename)

def registerHostDecline(fullname, phonenumber, useremail):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{fullname}, \nSorry to inform you that your Host Application has been Declined. Please contact us for more information! \n\nEmail: Support@areno.co.tz \nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        message = f"{fullname}, \nSorry to inform you that your Host Application has been Declined. Please contact us for more information! \n\nEmail: Support@areno.co.tz \nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send decline email for a host '
        pagename = 'sms_emails'
        generalErrorReport(error, 821, pagename)

def arenoBnbRequest(fullname, phonenumber, useremail, name):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi, {fullname}, \nYour booking for {name} has been submitted successfully. We will get back to you as soon as possible! \n\nThank You for choosing us.\nAreno Team",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = 'Success!'
        message = f"Hi, {fullname}, Your booking for {name} has been submitted successfully. We will get back to you as soon as possible! \n\nThank You for choosing us.\nAreno Team"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send success email for a customer who sent arenobnb bvooking request '
        pagename = 'sms_emails'
        generalErrorReport(error, 868, pagename)

def bookingRequestmessage(fullname, phonenumber, useremail, msg):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{msg}",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Hi! {fullname}!"
        message = f"{msg}"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send success email for user who sent a request in car rental post'
        pagename = 'sms_emails'
        generalErrorReport(error, 915, pagename)

def bookingRequestactionmessage(fullname, phonenumber, useremail, name):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"Hi! {fullname}, \nYour booking for {name} has been completed. For further information and concerns please contact us. Thank You for choosing us!",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Success!"
        message = f"Hi! {fullname}, \nYour booking for {name} has been completed. For further information and concerns please contact us. Thank You for choosing us!"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send success action completed email for user who sent a request in car rental post'
        pagename = 'sms_emails'
        generalErrorReport(error, 962, pagename)

def sendmessage_user(fullname, phonenumber, useremail, msg):
    #sending sms via beem
    try:
        url = beem_url

        data = {
            "source_addr": beem_source_addr,
            "encoding": 0,
            "message": f"{msg}",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f"{phonenumber}"
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
        subject = f"Hellow! {fullname}!"
        message = f"{msg}"
        from_email = from_email_title
        recipient_list = [useremail, ]

        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.reply_to = [from_email,]
            # Send email
            email.send()
            print('Email sent successfully!')
        except Exception as e:
            print('An error occurred while sending the email: {}'.format(str(e)))
    except:
        error = 'Failed to send user message from admin panel in userdetails view'
        pagename = 'sms_emails'
        generalErrorReport(error, 1009, pagename)



