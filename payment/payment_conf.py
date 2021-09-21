"""
Stripe API key (both sandbox or live) must be entered in STRIPE_API_KEY. 

PayPal Sandbox is by default True and in live/production servers, change this to False and update the API key if required.

Change the STRIPE_AMOUNT to your desired float with 2 decimal places (i.e. for £10, enter 1000 in the amount).
"""

from django.conf import settings

STRIPE = settings.STRIPE
PAYPAL = settings.PAYPAL

STRIPE_PRODUCTION = settings.STRIPE_PRODUCTION

STRIPE_API_KEY = settings.STRIPE_API_KEY
STRIPE_AMOUNT = settings.STRIPE_AMOUNT
STRIPE_CURRENCY = settings.STRIPE_CURRENCY
STRIPE_PRODUCT_NAME = settings.STRIPE_PRODUCT_NAME

STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET


PAYPAL_SANDBOX = settings.PAYPAL_SANDBOX
PAYPAL_CLIENT_KEY = settings.PAYPAL_CLIENT_KEY
PAYPAL_SECRET_KEY = settings.PAYPAL_SECRET_KEY
PAYPAL_AMOUNT = settings.PAYPAL_AMOUNT
PAYPAL_CURRENCY_CODE = settings.PAYPAL_CURRENCY_CODE


SUCCESS_TEMPLATE_PATH = settings.SUCCESS_TEMPLATE_PATH
FAIL_TEMPLATE_PATH = settings.FAIL_TEMPLATE_PATH
CANCEL_TEMPLATE_PATH = settings.CANCEL_TEMPLATE_PATH
DISCONTINUE_TEMPLATE_PATH = settings.DISCONTINUE_TEMPLATE_PATH