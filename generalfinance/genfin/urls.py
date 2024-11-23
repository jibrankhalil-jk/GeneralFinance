from django.urls import path
from . import views  

urlpatterns = [ 
    path('', views.Index,name='index'),    
    
    path('get-user/', views.get_user, name='get_user'),
    path('get_user_info/', views.get_user_info, name='get_user_info'),
    
    path('get-product/', views.get_product, name='get_product'),
    path('get_product_info/', views.get_product_info, name='get_product_info'),
    
    path('order_entry/', views.order_entry, name='order_entry'),
    
    # path('user/', views.createUser, name='user'),
    # path('add_user', views.add_user, name='add_user'),

    path('login', views.Login,name='login'),
    path('home', views.Home,name='home'),
    path('home/logout', views.Logout,name='home/logout'),
    path('home/entry', views.Entry,name='home/entry'),
    path('home/inventory', views.Inventory,name='home/inventory'),
    path('home/khata', views.Khata,name='home/khata'),
    path('home/analysis', views.Analysis,name='home/analysis'),
    path('home/settings', views.Settings,name='home/settings'), 
] 
