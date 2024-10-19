from django.contrib import admin
from . import models

admin.register(models.Transactions)
admin.register(models.Admin)
admin.register(models.Customer)
admin.register(models.Categories)
admin.register(models.Product)
admin.register(models.Loan)
admin.register(models.Sales)
admin.register(models.Item)
admin.register(models.LoanPayement)