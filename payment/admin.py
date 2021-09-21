from django.contrib import admin
from .models import PaymentOrder, Subscription, WebhookEvent
# Register your models here.

class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'active')

class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'payment_success')
    
class WebhookModelAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'event_type')

admin.site.register(PaymentOrder, PaymentModelAdmin)
admin.site.register(Subscription, SubscriptionModelAdmin)
admin.site.register(WebhookEvent, WebhookModelAdmin)