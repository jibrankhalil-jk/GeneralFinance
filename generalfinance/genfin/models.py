from django.db import models 
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import datetime
 
 
class Customer(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name =  models.CharField(max_length=50)
    phone_number =  models.IntegerField()
    adress =  models.TextField(max_length=500)
    last_login =  models.DateTimeField(default=datetime.now)
    status =  models.BooleanField(default=True)
    loan_status =   models.BooleanField(default=False)

class Admin(models.Model):
    ADMIN_ROLES = {
        "O": "Owner",
        "A": "Admin",
        "S": "SalesPerson",  
    }
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_name =  models.CharField(max_length=50)
    role = models.CharField(max_length=1, choices=ADMIN_ROLES)
    phone_number =  models.IntegerField()
    last_login =  models.DateTimeField(default=datetime.now)
    status =  models.BooleanField(default=True)

class Categories(models.Model): 
    categories_id = models.BigAutoField(primary_key=True)
    categorie_name = models.CharField(max_length=30)

class Product(models.Model): 
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=30)
    categorie_id = models.ForeignKey(Categories,on_delete=models.CASCADE)
    price = models.IntegerField()
    stock_quantity = models.IntegerField() 
    bar_code = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/images/",blank=True,null=True)
    quality = models.IntegerField()
    
class Transactions(models.Model): 
    transactions_id = models.BigAutoField(primary_key=True)
    transaction_type = models.CharField(max_length=30)
    transaction_date = models.DateField()
    total_amount = models.IntegerField()
     
    
class Sales(models.Model): 
    sales_id = models.BigAutoField(primary_key=True)
    sales_manager_id = models.ForeignKey(Admin,on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    total_amount = models.IntegerField()
    # items = models.
    user_id = models.ForeignKey(User ,on_delete=models.CASCADE)
    tid = models.ForeignKey(Transactions,on_delete=models.CASCADE)
    
class Sales(models.Model): 
    sales_manager_id = models.ForeignKey(Admin,on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    total_amount = models.IntegerField()
    # items = models.
    user_id = models.ForeignKey(User ,on_delete=models.CASCADE)
    tid = models.ForeignKey(Transactions,on_delete=models.CASCADE)
 
class Item(models.Model): 
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.IntegerField()
    sales_id = models.ForeignKey(Sales,on_delete=models.CASCADE)
    
    


