from django.urls import path
from . import views  

urlpatterns = [ 
    path('', views.Index,name='index'),    
    
    path('get-user/', views.get_user, name='get_user'),
    # path('entry/', views.entry_view, name='entry_view'),



    path('login', views.Login,name='login'),
    path('home', views.Home,name='home'),
    path('home/logout', views.Logout,name='home/logout'),
    path('home/entry', views.Entry,name='home/entry'),
    path('home/inventory', views.Inventory,name='home/inventory'),
    path('home/khata', views.Khata,name='home/khata'),
    path('home/analysis', views.Analysis,name='home/analysis'),
    path('home/settings', views.Settings,name='home/settings'), 
    path('add_user/', views.add_user, name='add_user'),
    
    path('add_customer/', views.add_customer, name='add_customer'),
    path('get_customer/', views.get_customer, name='get_customer'),
   
   #Inventory url path for adding product
    path('add_product/', views.add_product, name='add_product'),
    path('add_category/', views.add_category, name='add_category'),
   
  
] 
