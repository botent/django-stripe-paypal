from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class BasePayModel(models.Model):
    
    email = models.EmailField(verbose_name='Email', null=True)
    session_id = models.CharField(max_length=200, verbose_name='Session ID', null=True)
    payment_success = models.BooleanField(default=False, verbose_name='Payment Success', null=True)
    payment_service = models.CharField(max_length=200, verbose_name='Payment Service Name', null=True)
    additional_info = models.TextField(verbose_name='Entire Session Data', null=True)
    
    class Meta:
        abstract = True
class PaymentOrder(BasePayModel):
    name = models.ForeignKey(User,on_delete=models.DO_NOTHING, verbose_name='Name', null=True)
    date = models.DateField(verbose_name='Transaction Date', null=True)
    
    def __str__(self) -> str:
        return str(self.name)
    
class Subscription(BasePayModel):
    name = models.OneToOneField(User,on_delete=models.DO_NOTHING, verbose_name='Name', null=True)
    date = models.DateTimeField(verbose_name='Subscription Start Date', null=True)
    customer_id = models.CharField(max_length=200, verbose_name='Customer ID', null=True)
    active = models.BooleanField(default=False, verbose_name='Subscription Active')
    end_date = models.DateTimeField(verbose_name='Subscription End Date (if cancelled by User)', blank=True, null=True)
    subid = models.CharField(max_length=200, verbose_name='Subscription ID', null=True)
    
    def __str__(self) -> str:
        return str(self.name)
    
class WebhookEvent(models.Model):
    customer_id = models.CharField(max_length=200, verbose_name='Customer ID')
    event_type = models.CharField(max_length=200, verbose_name='Event Type')
    data_obj = models.JSONField(verbose_name='Data Object')
    event_info = models.JSONField(verbose_name='Full Event Data')
    
    def __str__(self) -> str:
        return str(self.customer_id)
    