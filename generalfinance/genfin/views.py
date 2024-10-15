from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def Index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('home')
 
def Login(request): 
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST": 
            userName = request.POST["username"]
            password = request.POST["password"]
            if len(userName) != 0 and len(password) != 0:
                if User.objects.filter(username=userName).exists():
                        user = authenticate(request, username=userName, password=password)
                        if user is not None:
                            try:
                                print('00-00'*20)
                                login(request, user)
                                print('00-00'*20)
                                return redirect('home') 
                            except Exception as e:
                                messages.error(request, '[',e,']')
                                # messages.error(request, 'Invalid email or password')
                                return render(request, 'registration/login.html')
                        else:
                            return render(request, 'registration/login.html')
                else:
                    messages.error(request, 'User dose not exist')
    return render(request, 'registration/login.html')

def Register(request): 
    if request.method == "POST": 
        if request.POST['email'] != '' and request.POST['password'] != '': 
            if User.objects.filter(email=request.POST['email']).exists():
                messages.info(request, 'Email already exists')
                return redirect('home')
            else:
                user = User.objects.create(email=request.POST['email'])
                user.set_password(request.POST['password'])
                user.save()
                messages.info(request, 'Account created successfully')
        return redirect('home')
    return render(request, 'registration/registration.html')

@login_required
def Logout(request):
    logout(request)
    return redirect('login')

@login_required
def Home(request):
    return render(request,'home/home.html',context={'active':'home'})

@login_required
def Entry(request):
    return render(request,'home/entry.html',context={'active':'entry'}) 

@login_required
def Inventory(request):
    return render(request,'home/inventory.html',context={'active':'inventory'})

@login_required
def Khata(request):
    return render(request,'home/khata.html',context={'active':'khata'})

@login_required
def Analysis(request):
    return render(request,'home/analysis.html',context={'active':'analysis'})

@login_required
def Settings(request):
    return render(request,'home/settings.html',context={'active':'settings'})


