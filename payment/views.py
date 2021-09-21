# Django Imports
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import RedirectView, View

# Model Imports
from .models import PaymentOrder, Subscription, WebhookEvent
from django.contrib.auth.models import User

# Other Imports
from .payment_conf import *
from datetime import datetime, timezone

# Third-party Imports
from stripe.api_resources import payment_method
import stripe
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest

# =============================================== #
#                    Views                        #
# =============================================== #

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
        if session.mode == 'subscription':
            order = Subscription.objects.get(id=session.client_reference_id)
            customer = stripe.Customer.retrieve(session.customer)
            order.session_id = session_id
            order.email = customer.email
            order.date = datetime.now()
            order.payment_success = True
            order.additional_info = session
            order.subid = session.subscription
            order.customer_id = customer.id
            order.active = True
            order.save()
        else:
            order = PaymentOrder.objects.get(id = session.client_reference_id)
            customer = stripe.Customer.retrieve(session.customer)
            order.session_id = session_id
            order.email = customer.email
            order.payment_service = 'Stripe'
            order.date = datetime.now()
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
        
        payment_order.email = order_response.result.payer.email_address
        payment_order.payment_service = 'PayPal'
        payment_order.payment_success = True
        payment_order.additional_info = order_response.result.__dict__
        payment_order.save()
        return render(request, SUCCESS_TEMPLATE_PATH)
    

class FailView(LoginRequiredMixin, TemplateView):
    
    def get(self, request):
        try:
            try:
                obj = Subscription.objects.get(name=request.user)
                obj.delete()
            except:
                obj = PaymentOrder.objects.get(name=request.user)
                obj.delete()
        except Exception as e:
            raise e
        return render(request, FAIL_TEMPLATE_PATH)
    

# Subscription Views
class StripeSubscription(LoginRequiredMixin, View):

    stripe_url_prefix = 'http://'
    if STRIPE_PRODUCTION:
        stripe_url_prefix = 'https://'
        
    def get(self, request, priceid):
        host = request.get_host()
        sub_order = Subscription.objects.create(name=request.user)
        sub_order.refresh_from_db()
        paymentid = sub_order.id
        session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items = [
                {
                    'price': priceid,
                    'quantity': 1,
                }
            ],
            mode = 'subscription',
            client_reference_id = paymentid,
            success_url = '{}{}/payment/stripe-success/{{CHECKOUT_SESSION_ID}}'.format(self.stripe_url_prefix, host),
            cancel_url='{}{}{}'.format(self.stripe_url_prefix, host, reverse('fail')),
        )
        return redirect(session.url)

class StripeSubscriptionCancel(LoginRequiredMixin, View):
    # Cancel Immediately
    def get(self, request):
        user = request.user
        sub_obj = Subscription.objects.get(name=user)
        sub_id = sub_obj.subid
        sub_obj.end_date = datetime.now()
        sub_obj.active = False
        sub_obj.save()
        stripe.Subscription.delete(sub_id)
        return render(request, CANCEL_TEMPLATE_PATH)

class StripeSubscriptionModify(LoginRequiredMixin, View):
    # Cancel at the end of Period
    def get(self, request):
        user = request.user
        sub_obj = Subscription.objects.get(name=user)
        sub_id = sub_obj.subid
        subinfo = stripe.Subscription.retrieve(sub_id)
        end_date = subinfo['current_period_end']
        e_date = datetime.fromtimestamp(end_date / 1.0, tz=timezone.utc)
        sub_obj.end_date = e_date
        sub_obj.save()
        stripe.Subscription.modify(sub_id, cancel_at_period_end=True)
        return render(request, DISCONTINUE_TEMPLATE_PATH)


class StripeWebhook(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.headers['STRIPE_SIGNATURE']
        endpoint_secret = STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e: 
            raise e
        except stripe.error.SignatureVerificationError as e:
            raise e
        
        eventlist = [
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
            
        ]
        if event['type'] in eventlist:
            WebhookEvent.objects.create(
                customer_id=event['data']['object']['customer'],
                event_type=event['type'],
                data_obj=event['data']['object'],
                event_info=event
            )
            

