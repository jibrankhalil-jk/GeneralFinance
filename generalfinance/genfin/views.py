from django.shortcuts import render,redirect
from django.http import HttpRequest


def Index(request):
    return redirect('login')

def Login(request): 
    if request.method == "POST": 
        # print(HttpRequest.path.split('/')[1])
        print(request.POST['email'])
        print(request.POST['password'])
        return redirect('home')
    return render(request, 'login.html')

def Home(request):
    return render(request,'home/home.html',context={'active':'home'})

def Entry(request):
    return render(request,'home/entry.html',context={'active':'entry'}) 

def Inventory(request):
    return render(request,'home/inventory.html',context={'active':'inventory'})

def Khata(request):
    return render(request,'home/khata.html',context={'active':'khata'})

def Analysis(request):
    return render(request,'home/analysis.html',context={'active':'analysis'})

def Settings(request):
    return render(request,'home/settings.html',context={'active':'settings'})


