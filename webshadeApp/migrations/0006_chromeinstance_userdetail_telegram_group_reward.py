# Generated by Django 5.1.2 on 2025-03-12 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshadeApp', '0005_userdetail_telegram_reward'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChromeInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255, unique=True)),
                ('pid', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='userdetail',
            name='telegram_group_reward',
            field=models.BooleanField(default=False),
        ),
    ]
