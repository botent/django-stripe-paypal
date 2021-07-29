# Django-Stripe-PayPal (DSP)
DSP is a Django app to accept payments (one-time) from Paypal and Stripe.
(Will soon add subscriptions and payouts)



# Quick Setup

1.  Add "payment" to your INSTALLED_APPS setting like this::

    ```
	   INSTALLED_APPS = [
	        ...
	        'payment',
		    ]

2. Include the payment URLconf in your project ```urls.py ```like this::

    ```path('payment/', include('payment.urls')),``` and make migrations.
3. In ```settings.py``` add the following -
	 
	```
	STRIPE  =  True
	PAYPAL  =  True

	STRIPE_PRODUCTION = False

	STRIPE_API_KEY  =  ''
	STRIPE_AMOUNT  =  10000
	STRIPE_CURRENCY  =  'gbp'
	STRIPE_PRODUCT_NAME  =  ''

	PAYPAL_SANDBOX  =  True
	PAYPAL_CLIENT_KEY  =  ''
	PAYPAL_SECRET_KEY  =  ''
	PAYPAL_AMOUNT  =  10
	PAYPAL_CURRENCY_CODE  =  'gbp'
	  
	SUCCESS_TEMPLATE_PATH  =  'success.html'

	FAIL_TEMPLATE_PATH  =  'fail.html'
	```
	
4. While using the ```checkout``` views, make sure the URL has string argument as shown on the template file using (was made to ease the process and is an integral part) -

	```
	<div>

	<a  href="{% url 'checkout' 'Stripe' %}">Stripe Checkout</a>
	<a  href="{% url 'checkout' 'Paypal' %}">PayPal Checkout</a>

	</div>
	```

**STRIPE** and **PAYPAL** defaults to ```True``` i.e. both the payment services are being used. Change according to your needs. For **STRIPE_AMOUNT**, use the non-decimal representation of currency (i.e. for £10, input 1000) and for **PAYPAL_AMOUNT**, use the standard notation (i.e. £10 as 10 or 10.00).

**SUCCESS_TEMPLATE_PATH** and **FAIL_TEMPLATE_PATH** refer to the templates for payment success and fail/cancel views respectively. Add your custom path here.

The  **checkout** and **success** views use user object to store records, so ensure that the user is signed in before processing the checkout (```LoginRequiredMixin``` is in place, but consider this a friendly reminder) - make sure your ```login_url``` is configured properly in ```settings.py```

## Live/Production Guide

**PAYPAL_SANDBOX** defaults to ```True``` and in live/production, change it to ```False``` and change **STRIPE_PRODUCTION** to ```True```
