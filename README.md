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

    ```path('payment/', include('payment.urls')),```
3. In ```settings.py``` add the following -
	 
	```
	STRIPE  =  True
	PAYPAL  =  True

	STRIPE_PRODUCTION = False

	STRIPE_API_KEY  =  ''
	STRIPE_AMOUNT  =  10000
	STRIPE_CURRENCY  =  'gbp'
	STRIPE_PRODUCT_NAME  =  ''
    STRIPE_WEBHOOK_SECRET = ''    

	PAYPAL_SANDBOX  =  True
	PAYPAL_CLIENT_KEY  =  ''
	PAYPAL_SECRET_KEY  =  ''
	PAYPAL_AMOUNT  =  10
	PAYPAL_CURRENCY_CODE  =  'gbp'
	  
	SUCCESS_TEMPLATE_PATH  =  'template_success.html' or 'appname/template_success.html'
	FAIL_TEMPLATE_PATH  =  'template_fail.html' or 'appname/template_fail.html'
    # For users who cancelled their subscriptions and continue till their period ends
    DISCONTINUE_TEMPLATE_PATH = 'template_discontinue.html' or 'appname/template_discontinue.html' 
    # For users who cancelled their subscriptions IMMEDIATELY
    CANCEL_TEMPLATE_PATH = 'template_cancel.html' or 'appname/template_cancel.html'
	```
	
4. Migrate the DB (i.e. ``python manage.py migrate`` )
5. While using the ```checkout``` views, make sure the URL has string argument as shown on the template file using (was made to ease the process and is an integral part) -

	```
	<div>

	<a  href="{% url 'checkout' 'Stripe' %}">Stripe Checkout</a>
	<a  href="{% url 'checkout' 'Paypal' %}">PayPal Checkout</a>

	</div>
	```

**STRIPE** and **PAYPAL** defaults to ```True``` i.e. both the payment services are being used. Change according to your needs. For **STRIPE_AMOUNT**, use the non-decimal representation of currency (i.e. for £10, input 1000) and for **PAYPAL_AMOUNT**, use the standard notation (i.e. £10 as 10 or 10.00).

**SUCCESS_TEMPLATE_PATH** and **FAIL_TEMPLATE_PATH** refer to the templates for payment success and fail/cancel views respectively. Add your custom path here.

The  **checkout** and **success** views use user object to store records, so ensure that the user is signed in before processing the checkout (```LoginRequiredMixin``` is in place, but consider this a friendly reminder) - make sure your ```login_url``` is configured properly in ```settings.py```

## Subscriptions Guide
1. ```StripeSubscription``` view is responsible for initiating a transaction. In your templates, you need to provide parameter ```priceid``` which you can obtain from <https://dashboard.stripe.com/products> as ->

   ```<a href="{% url 'stripe-sub' 'priceid' %}">Premium</a>``` 
2. The user is then redirected to Stripe URL and an object is created in the **Subscription** Model which gets updated/deleted upon success/fail respectively.

3. ```StripeWebhook``` view records the following events emitted by the Stripe Webhook --

```
            'invoice.finalized',
            'invoice.payment_succeeded',
            'invoice.payment_action_required',
            'invoice.payment_failed',
            'invoice.updated',
            'invoice.paid',
            'payment_intent.succeeded',
            'payment_intent.failed',
            'payment_intent.canceled',
            'payment_intent.created',
            'customer.subscription.created',
            'customer.subscription.deleted',
            'customer.subscription.updated',
            'customer.source.expiring',
            'charge.succeeded',
            'charge.failed',
```

4. ```StripeSubscriptionCancel``` view ends the subscription immediately and sets Active state to False for the User
5. ```StripeSubscriptionModify``` view ends the subscription at the period end date. [Will soon update the ACTIVE status code]

## Templates Guide (No offence, pros)
 ```
	Project
	|
	|
	|___App1
	    |
	    |
	    |___Templates
	        |
	        |
	        |___App1
	            |___template1.html
```

If you follow the above directory structure, in ```settings.py``` under ```SUCCESS_TEMPLATE_PATH``` and ```FAIL_TEMPLATE_PATH``` input as - ```App1/template1.html```.

For the users with ```templates``` in root, proceed as usual! 

## Live/Production Guide

**PAYPAL_SANDBOX** defaults to ```True``` and in live/production, change it to ```False``` and change **STRIPE_PRODUCTION** to ```True```

