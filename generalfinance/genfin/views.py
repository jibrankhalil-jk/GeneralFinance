from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . import forms, models 
from django.http import JsonResponse
from .models import User, Product, Categories
from django.utils.crypto import get_random_string
from .models import Customer

def Index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('home')

# def createUser(request):
#     username = 'admin'
#     username = username.toLower()
#     user = User.objects.create(username=username,email=f"{username}@gmail.com")
#     user.set_password(username)
#     user.save()
#     customer = models.Customer.objects.create(user_id=user ,customer_name =username,phone_number =3001234567,address = "Lahore, Pakistan")
#     customer.save()
#     return render(request,'home/home.html')


def Login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            userName = request.POST["username"]
            password = request.POST["password"]
            if len(userName) != 0 and len(password) != 0:
                if User.objects.filter(username=userName).exists():
                    user = authenticate(
                        request, username=userName, password=password)
                    if user is not None:
                        try:
                            login(request, user)
                            return redirect('home')
                        except Exception as e:
                            messages.error(request, f'Error: {e}')
                            return render(request, 'registration/login.html')
                    else:
                        messages.error(request, 'Invalid username or password')
                        return render(request, 'registration/login.html')
                else:
                    messages.error(request, 'User does not exist')
                    return render(request, 'registration/login.html')
            else:
                messages.error(
                    request, 'Username and password cannot be empty')
                return render(request, 'registration/login.html')
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


def add_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')
        address = request.POST.get('address')
        username = get_random_string(10)

        # Create the user
        user = User.objects.create_user(username,number,address)
        user.first_name = name
        user.save()
        return JsonResponse({'success': True, 'user': {'name': name, 'number': number,'address': address}})
    return JsonResponse({'success': False})

@login_required
def Logout(request):
    logout(request)
    return redirect('login')


@login_required
def Home(request):
    chart_data = [
        {"label": "Direct", "value": 50, "color": "text-primary"},
        {"label": "Social", "value": 30, "color": "text-success"},
        {"label": "Referral", "value": 15, "color": "text-info"}
    ]
    current_user = request.user
    return render(request, 'home/home.html', context={'active': 'home', 'username': current_user, 'chart_data': chart_data})


@login_required
def Entry(request):
    # sales_form = forms.SalesEntryForm()
    return render(request, 'home/entry.html', context={'active': 'entry', })


@login_required
def Inventory(request):
    return render(request, 'home/inventory.html', context={'active': 'inventory'})


@login_required
def Khata(request):
    return render(request, 'home/khata.html', context={'active': 'khata'})


@login_required
def Analysis(request):
    return render(request, 'home/analysis.html', context={'active': 'analysis'})


@login_required
def Settings(request):
    return render(request, 'home/settings.html', context={'active': 'settings'})


def custom_404_view(request): 
    return render(request, '404.html')


# -------------------------------------- Request views --------------------------------------
 

@login_required
def get_user(request):
    username_prefix = request.GET["username"]
    if username_prefix:
        customers = models.User.objects.filter(username__startswith=username_prefix)
        customer_usernames = [customer.username for customer in customers]
    else:
        customer_usernames = []
    return JsonResponse({"data": customer_usernames})


def unknown(request):
    return render(request, '404.html')

@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')
        address = request.POST.get('address')
        username = get_random_string(10)

        # Create the user
        user = User.objects.create_user(username=username, password='defaultpassword')
        user.first_name = name
        user.save()

        # Create the customer
        customer = Customer.objects.create(user_id=user, customer_name=name, phone_number=number, address=address)
        return JsonResponse({'success': True, 'user': {'id': customer.id, 'name': name, 'number': number, 'address': address}})
    return JsonResponse({'success': False})
# @login_required
# def get_customer(request):
#     username = request.GET.get('username')
#     if not username:
#         return JsonResponse({'success': False, 'error': 'Username parameter is missing or empty'})

#     customers = Customer.objects.filter(user_id__username__icontains=username)
   
#     return JsonResponse({'data': [customers.name,customers.phone_number,customers.address]})
@login_required
def get_customer(request):
    username = request.GET.get('username')
    user_id = request.GET.get('user_id')

    if username:
        customers = Customer.objects.filter(user_id__username__icontains=username)
        data = [
            {
                'id': customer.id,
                'name': customer.customer_name,
                'address': customer.address,
                'phone': customer.phone_number,
            }
            for customer in customers
        ]
        return JsonResponse({'success': True, 'data': data})

    if user_id:
        try:
            customer = Customer.objects.get(id=user_id)
            data = {
                'id': customer.id,
                'name': customer.customer_name,
                'address': customer.address,
                'phone': customer.phone_number,
            }
            return JsonResponse({'success': True, 'data': data})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})

    return JsonResponse({'success': False, 'error': 'No valid parameters provided'})





#Inventory Product 

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        # expire_date = request.POST.get('expire_date')
        stock_quantity = int(request.POST.get('quantity'))
        category_id = request.POST.get('category')

        category = Categories.objects.get(id=category_id)
        product, created = Product.objects.get_or_create(
            product_name=name,
            categorie_id=category,
            defaults={'price': price, 'stock_quantity': stock_quantity}
        )

        if not created:
            product.stock_quantity += stock_quantity
            product.save()

        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': name,
                'price': price,
                'quantity': product.stock_quantity,
                'category': category.categorie_name
            },
            'created': created
        })
    return JsonResponse({'success': False})
@login_required
def inventory(request):
    categories = Categories.objects.all()
    return render(request, 'inventory.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = Categories.objects.create(categorie_name=name)
        return JsonResponse({'success': True, 'category': {'id': category.id, 'name': name}})
    return JsonResponse({'success': False})