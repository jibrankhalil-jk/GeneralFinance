from django.urls import path,include
from . import views

urlpatterns = [ 
    path('', views.Index,name='index'),
    path('login', views.Login,name='login'),
    path('home', views.Home,name='home'),
    
    path('home/logout', views.Logout,name='home/logout'),
    

    path('home/entry', views.Entry,name='home/entry'),
    path('home/inventory', views.Inventory,name='home/inventory'),
    path('home/khata', views.Khata,name='home/khata'),
    path('home/analysis', views.Analysis,name='home/analysis'),
    path('home/settings', views.Settings,name='home/settings'),
] 
