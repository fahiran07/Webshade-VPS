# Generated by Django 5.1.2 on 2025-03-18 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webshadeAdmin', '0005_requesthandlingadmin_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requesthandlingadmin',
            name='active_task',
        ),
    ]
