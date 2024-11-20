from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . import forms, models
from django.http import JsonResponse
from django.contrib.auth import authenticate
# from .models import User
from django.utils.crypto import get_random_string


def Index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('home')

# def createCategorie(request):
#     categorie = models.Categories.objects.create(categorie_name="Books")
#     categorie.save()
#     return render(request,'home/home.html')

# def createUser(request):
#     username = 'naeem'.lower()
#     pn = 3125452445
#     ad = 'gilgi,Pakistan'
#     username = username.lower()
#     user = User.objects.create(username=username,email=f"{username}@gmail.com")
#     user.set_password(f"{username}@gmail.com")
#     user.save()
#     customer = models.Customer.objects.create(user_id=user ,customer_name =username,phone_number=pn,address = ad)
#     customer.save()
#     return render(request,'home/home.html')

# def add_user(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         number = request.POST.get('number')
#         address = request.POST.get('address')
#         username = get_random_string(10)

#         # Create the user
#         user = User.objects.create_user(username, number, address)
#         user.first_name = name
#         user.save()
#         return JsonResponse({'success': True, 'user': {'name': name, 'number': number, 'address': address}})
#     return JsonResponse({'success': False})


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
    return render(request, 'home/entry.html', context={'active': 'entry'})


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
        customers = models.User.objects.filter(
            username__startswith=username_prefix)[:4]
        customer_usernames = [customer.username for customer in customers]
    else:
        customer_usernames = []
    return JsonResponse({"data": customer_usernames})


@login_required
def get_user_info(request):
    user_name = request.GET["username"]
    if user_name:
        customer = User.objects.filter(username=user_name).first()
        # print("???????? ",customer)

        if customer:
            try:
                data = models.Customer.objects.filter(user_id=customer).first()
                print("???????? ", data.phone_number)
                if data:
                    return JsonResponse({"data": [data.customer_name, data.phone_number]})
            except Exception as e:
                print("???????? ", e)
        else:
            pass
    return JsonResponse({"data": []})


@login_required
def get_product(request):
    product_prefix = request.GET["product"]
    print('>>>>>>> ', product_prefix)
    if product_prefix:
        found_products = models.Product.objects.filter(
            product_name__startswith=product_prefix)[:5]
        product_names = [prdct.product_name for prdct in found_products]
    else:
        product_names = []
    return JsonResponse({"data": product_names})


@login_required
def get_product_info(request):
    prouct_name = request.GET["product"]
    if prouct_name:
        try:
            found_products = models.Product.objects.filter(
                product_name=prouct_name).first()
            # print(type(found_products.stock_quantity))
            if found_products:
                if int(str(found_products.stock_quantity)) >= 1:
                    return JsonResponse({"data": [found_products.pk,
                                                  found_products.product_name,
                                                  found_products.price,
                                                  found_products.stock_quantity]})
                else:
                    return JsonResponse({"data": [], "message": 'stock full'})
        except Exception as e:
            print("+_+_+_+_+_+_+_+_++_+ ", e)
        else:
            pass
    # print("+++++++++ no product +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return JsonResponse({"data": [], "message": 'no product'})


@login_required
def order_entry(request): 
    username  = request.GET.get('user');
    items = [] 
    for key, value in request.GET.items():
        if key.startswith('items['):
            indices = key[:-2].split('[')[1:3]  # Get the two indices
            if len(indices) == 2:  # Only process valid item keys
                item_values = request.GET.getlist(key)
                if item_values:
                    items.append({
                        'id': item_values[0],
                        'name': item_values[1],
                        'price': item_values[2], 
                        'quantity': item_values[3]
                    })
    for item in items:
        curr_product = models.Product.objects.filter(id=item['id']).first()
        if curr_product:
            curr_product.stock_quantity -= int(item['quantity'])
            curr_product.save()
        break
    return JsonResponse({"data": [], "message": 'no product'})
