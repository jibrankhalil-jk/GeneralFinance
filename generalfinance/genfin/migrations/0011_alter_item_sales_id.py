# Generated by Django 5.1.2 on 2024-11-23 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0010_remove_item_itesms_item_sales_id_alter_admin_role_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='sales_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genfin.sales'),
        ),
    ]