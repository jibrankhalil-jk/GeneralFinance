# Generated by Django 5.1.2 on 2024-11-20 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfin', '0007_alter_product_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(max_length=500),
        ),
    ]
