# Generated by Django 5.1.2 on 2024-11-20 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0004_alter_product_product_name_remove_sales_items_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(max_length=200),
        ),
    ]
