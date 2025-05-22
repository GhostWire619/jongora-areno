import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env('devkeys.env')
# Beem Sms API

beem_url = env('beem_url')
beem_source_addr = env('beem_source_addr')
beem_username = env('beem_username')
beem_password = env('beem_password')


# Email Key details

from_email_title = f'ARENO <info@areno.co.tz>'
email_reply_to = 'no-reply@areno.co.tz'

# VAT - Calculate the new price with 18% VAT
vat = 1.18 # 1.18 represents the original price (100%) plus 18% (100% + 18%)) 

