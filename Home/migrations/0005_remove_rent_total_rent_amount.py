# Generated by Django 4.1 on 2025-04-25 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0004_alter_wishlist_unique_together_alter_wishlist_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rent',
            name='total_rent_amount',
        ),
    ]
