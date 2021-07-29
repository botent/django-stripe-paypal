from os import name
from django.urls import path
from .views import *

urlpatterns = [
    path('checkout/<service>', CheckoutView.as_view(), name='checkout'),
    path('stripe-success/<str:session_id>', StripeSuccessView.as_view(), name='stripe-success'),
    path('paypal-success', PaypalSuccessView.as_view(), name='paypal-success'),
    path('failed', FailView.as_view(), name='fail')
    
]
