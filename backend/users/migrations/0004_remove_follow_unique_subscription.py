# Generated by Django 3.2 on 2023-08-07 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230805_2358'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_subscription',
        ),
    ]
