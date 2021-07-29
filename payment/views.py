from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from .payment_conf import *
from django.views.generic import RedirectView, View
from .models import PaymentOrder
import stripe
from datetime import date
from django.urls import reverse
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

stripe.api_key = STRIPE_API_KEY
    
if PAYPAL_SANDBOX:
    environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_KEY, client_secret=PAYPAL_SECRET_KEY)
else:
    environment = LiveEnvironment(client_id=PAYPAL_CLIENT_KEY, client_secret=PAYPAL_SECRET_KEY)
        
client = PayPalHttpClient(environment)



class CheckoutView(LoginRequiredMixin, View):
    
    stripe_url_prefix = 'http://'
    paypal_url_prefix = 'http://'
    if STRIPE_PRODUCTION:
        stripe_url_prefix = 'https://'
    if not PAYPAL_SANDBOX:
        paypal_url_prefix = 'https://'
    
    def get(self, request, service):
        if STRIPE and PAYPAL:
            if service.lower() == 'stripe':
                return redirect(self.stripecheckout(request))
            elif service.lower() == 'paypal':
                return redirect(self.paypalcheckout(request))
        elif STRIPE and not PAYPAL:
            return redirect(self.stripecheckout(request))
        elif not STRIPE and PAYPAL:
            return redirect(self.paypalcheckout(request))
        else:
            raise Exception('YOU CHOSE NEITHER PAYPAL NOR STRIPE.')
    
    def stripecheckout(self, request):
        host = request.get_host()
        payment_order = PaymentOrder.objects.create(name=request.user)
        payment_order.refresh_from_db()
        paymentid = payment_order.id
        session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': STRIPE_CURRENCY,
                'product_data': {
                    'name': STRIPE_PRODUCT_NAME,
                },
                'unit_amount': STRIPE_AMOUNT,
            },
            'quantity': 1,
        }],
        mode='payment',
        client_reference_id = paymentid,
        success_url='{}{}/payment/stripe-success/{{CHECKOUT_SESSION_ID}}'.format(self.stripe_url_prefix, host),
        cancel_url='{}{}{}'.format(self.stripe_url_prefix, host, reverse('fail')),
        )
        return session.url
    
    def paypalcheckout(self, request):
        host = request.get_host()
        order = OrdersCreateRequest()
        payment_order = PaymentOrder.objects.create(name=request.user)
        payment_order.refresh_from_db()
        paymentid = payment_order.id
        order.prefer('return=representation')

        order.request_body(
            {
                "intent": "CAPTURE",
                "application_context": {
                    "return_url": '{}{}{}'.format(self.paypal_url_prefix, host, reverse('paypal-success')),
                    "cancel_url": "{}{}{}".format(self.paypal_url_prefix, host, reverse('fail')),
                },
                "purchase_units": [
                    {
                        "reference_id": paymentid,
                        "amount": {
                            "currency_code": PAYPAL_CURRENCY_CODE,
                            "value": PAYPAL_AMOUNT
                        }
                    }
                ]
            }
        )
        order_response = client.execute(order)
        paypal_url = [link.href for link in order_response.result.links][1]
        request.session['order_id'] = order_response.result.id
        return paypal_url
    
class StripeSuccessView(LoginRequiredMixin, View):
    
    def get(self, request, session_id):
        session = stripe.checkout.Session.retrieve(session_id)
        order = PaymentOrder.objects.get(id = session.client_reference_id)
        customer = stripe.Customer.retrieve(session.customer)
        order.session_id = session_id
        order.name = customer.name
        order.email = customer.email
        order.payment_service = 'Stripe'
        order.date = date.today()
        order.payment_success = True
        order.additional_info = session
        order.save()
        return render(request, SUCCESS_TEMPLATE_PATH)

    
class PaypalSuccessView(LoginRequiredMixin, View):
    
    def get(self, request):
        orderid = request.session.get('order_id')
        order = OrdersCaptureRequest(orderid)
        order_response = client.execute(order)
        
        paymentid = order_response.result['purchase_units'][0]['reference_id']
        payment_order = PaymentOrder.objects.get(id=paymentid)
        
        payment_order.name = order_response.result['purchase_units'][0]['shipping']['name']['full_name']
        payment_order.email = order_response.result.payer.email_address
        payment_order.payment_service = 'PayPal'
        payment_order.payment_success = True
        payment_order.additional_info = order_response.result.__dict__
        payment_order.save()
        return render(request, SUCCESS_TEMPLATE_PATH)
    

class FailView(LoginRequiredMixin, TemplateView):
    
    def get(self, request):
        return render(request, FAIL_TEMPLATE_PATH)