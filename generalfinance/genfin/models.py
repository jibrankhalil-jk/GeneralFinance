from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save 
from django.utils.timezone import datetime
from django.utils import timezone


class Transactions(models.Model):
    transaction_type = models.CharField(max_length=30, default="Cash")
    transaction_date = models.DateField(default=timezone.now)
    total_amount = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

class Admin(models.Model):
    ADMIN_ROLES = [
        ('admin', 'Administrator'),
        ('user', 'User'),
        ('guest', 'Guest'),
    ]
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ADMIN_ROLES, default="user")
    phone_number = models.BigIntegerField()
    last_login = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)

class Customer(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50)
    phone_number = models.BigIntegerField()
    address = models.TextField(max_length=500)
    last_login = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    loan_status = models.BooleanField(default=False)
class Categories(models.Model): 
    categorie_name = models.CharField(max_length=30)

class Product(models.Model): 
    categorie_id = models.ForeignKey(Categories, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=30)
    price = models.IntegerField(default=0)
    # expire_date = models.DateField(default=datetime.now)
    stock_quantity = models.IntegerField(default=0)
    
    bar_code = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to="products/images/", blank=True, null=True)
    quality = models.IntegerField(default=1)


class Loan(models.Model): 
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    previous_amount = models.IntegerField(default=0)

class Sales(models.Model): 
    sales_manager_id = models.ForeignKey(Admin, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now)
    total_amount = models.IntegerField(default=0)
    items = models.ManyToManyField(Product)
    user_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    transactions_id = models.ForeignKey(Transactions, on_delete=models.CASCADE)


class Item(models.Model):  
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    subtotal = models.IntegerField(default=0)


class LoanPayement(models.Model): 
    sales_manager_id = models.ForeignKey(Admin, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now)
    total_amount = models.IntegerField(default=0)
    payement_type = models.CharField(max_length=30, default="Cash")
    user_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    


