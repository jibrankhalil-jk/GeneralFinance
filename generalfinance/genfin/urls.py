from django.urls import path

from . import apis
from . import views

urlpatterns = [
    path('', views.redirect_to_home, name='index'),

    path('home', views.Home, name='home'),
    path('login', views.Login, name='login'),
    path('home/logout', views.Logout, name='home/logout'),
    path('home/entry', views.Entry, name='home/entry'),
    path('home/inventory', views.Inventory, name='home/inventory'),
    path('home/khata', views.Khata, name='home/khata'),
    path('home/analysis', views.Analysis, name='home/analysis'),
    path('home/settings', views.Settings, name='home/settings'),

    path('add_customer/', views.add_customer, name='add_customer'),
    path('get_customer/', views.get_customer, name='get_customer'),

    # Inventory url path for adding product
    path('add_product/', views.add_product, name='add_product'),
    path('add_category/', views.add_category, name='add_category'),

    # --------- Entry Page  ------------------------
    path('get-user/', apis.get_user, name='get_user'),
    # path('get_user_info/', views.get_user_info, name='get_user_info'),
    path('get-product/', apis.get_product, name='get_product'),
    path('get_product_info/', apis.get_product_info, name='get_product_info'),
    path('order_entry/', apis.order_entry, name='order_entry'),



    path('user/', views.createUser, name='user'),
    # path('add_user', views.add_user, name='add_user'),

    # path('home/ana', analysis.get_sales_of_month, name='add_user'),



]
