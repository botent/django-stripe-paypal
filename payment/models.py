from django.db import models

# Create your models here.

class PaymentOrder(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name', null=True)
    email = models.EmailField(verbose_name='Email', null=True)
    session_id = models.CharField(max_length=200, verbose_name='Session ID', null=True)
    payment_success = models.BooleanField(default=False, verbose_name='Payment Success', null=True)
    payment_service = models.CharField(max_length=200, verbose_name='Payment Service Name', null=True)
    additional_info = models.TextField(verbose_name='Entire Session Data', null=True)
    date = models.DateField(verbose_name='Transaction Date', null=True)
    
    def __str__(self) -> str:
        return str(self.name)