# Generated by Django 5.1.2 on 2025-03-06 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='login_number',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50)),
                ('login_by', models.CharField(blank=True, default='', max_length=50)),
                ('status', models.CharField(default='no login', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='reward_price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_24', models.IntegerField(default=50)),
                ('amount_48', models.IntegerField(default=30)),
                ('amount_72', models.IntegerField(default=20)),
                ('amount_96', models.IntegerField(default=10)),
                ('amount_120', models.IntegerField(default=10)),
                ('amount_144', models.IntegerField(default=10)),
                ('amount_168', models.IntegerField(default=10)),
                ('server_status', models.BooleanField(default=False)),
            ],
        ),
    ]
