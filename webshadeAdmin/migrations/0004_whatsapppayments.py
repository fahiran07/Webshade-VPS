# Generated by Django 5.1.2 on 2025-03-16 19:23

import webshadeAdmin.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshadeAdmin', '0003_requesthandlingadmin_active_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='whatsappPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_id', models.CharField(max_length=50)),
                ('amount', models.IntegerField(default=0)),
                ('releaser', models.CharField(max_length=50)),
                ('date', models.CharField(default=webshadeAdmin.models.get_date_string, max_length=50)),
                ('time', models.CharField(default=webshadeAdmin.models.get_time_string, max_length=50)),
            ],
        ),
    ]
