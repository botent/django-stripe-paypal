# Generated by Django 3.2.5 on 2021-09-21 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_alter_paymentorder_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=200, verbose_name='Customer ID')),
                ('event_type', models.CharField(max_length=200, verbose_name='Event Type')),
                ('data_obj', models.JSONField(verbose_name='Data Object')),
                ('event_info', models.JSONField(verbose_name='Full Event Data')),
            ],
        ),
    ]
