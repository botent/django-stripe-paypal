# Generated by Django 3.2.5 on 2021-07-29 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='date',
            field=models.DateField(null=True, verbose_name='Transaction Date'),
        ),
    ]