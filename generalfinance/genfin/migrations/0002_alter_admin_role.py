# Generated by Django 5.1.2 on 2024-11-07 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('user', 'User'), ('guest', 'Guest')], default='user', max_length=10),
        ),
    ]
