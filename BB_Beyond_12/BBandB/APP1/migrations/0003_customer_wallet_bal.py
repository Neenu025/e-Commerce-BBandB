# Generated by Django 4.2.4 on 2023-11-18 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP1', '0002_product_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='wallet_bal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
