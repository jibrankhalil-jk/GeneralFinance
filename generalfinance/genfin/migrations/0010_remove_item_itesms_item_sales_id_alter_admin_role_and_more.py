# Generated by Django 5.1.2 on 2024-11-23 12:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0009_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='itesms',
        ),
        migrations.AddField(
            model_name='item',
            name='sales_id',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='genfin.sales'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('user', 'User'), ('guest', 'Guest')], default='user', max_length=10),
        ),
        migrations.AlterField(
            model_name='categories',
            name='categorie_name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(max_length=30),
        ),
        migrations.RemoveField(
            model_name='sales',
            name='items',
        ),
        migrations.AddField(
            model_name='sales',
            name='items',
            field=models.ManyToManyField(to='genfin.product'),
        ),
    ]
