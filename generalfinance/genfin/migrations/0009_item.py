# Generated by Django 5.1.2 on 2024-11-23 12:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0008_alter_product_product_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itesms', models.JSONField(default=list)),
                ('quantity', models.IntegerField(default=0)),
                ('subtotal', models.IntegerField(default=0)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genfin.product')),
            ],
        ),
    ]
