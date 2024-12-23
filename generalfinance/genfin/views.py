from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . import  models, apis,analysis
from django.http import JsonResponse
from django.contrib.auth import authenticate     
import pandas as pd
import datetime
from django.utils.crypto import get_random_string



def Index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('home')


def createCategorie(request):
    categorie = models.Categories.objects.create(categorie_name="Books")
    categorie.save()
    return render(request, 'home/home.html')


def createUser(request):

    current_logedin_user = User.objects.filter(username=request.user).first()
    if current_logedin_user:
        sales_manager = models.Admin.objects.filter(
            user_id=current_logedin_user).first()

        df = pd.read_csv(
            '/Users/jibrankhalil/Dev/Projects/GeneralFinance/SourceCode/genfin/scrapping_data/entry/final.csv')
        for _, d in df.iterrows():
            date = datetime.datetime.strptime(
                d['date'].split('+')[0], '%Y-%m-%d %H:%M:%S.%f')
            items = d['items']
            user_id = d['user_id'],
            total = d['total']
            tn_type = d['transaction_type']

            current_transaction = models.Transactions.objects.create(total_amount=total, status=0, transaction_date=date,transaction_type=tn_type)
            current_transaction.save()

            c_user = models.Customer.objects.filter(id=user_id[0]).first()
            if c_user:
                sale = models.Sales.objects.create(user_id=c_user, date_time=date, items=items,sales_manager_id=sales_manager, total_amount=total, transactions_id=current_transaction)
                sale.save()
        return JsonResponse({'data': f"done"})
    return JsonResponse({'data': user_id})



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
    data = apis.get_today_sales_data()
    sources = apis.get_today_payement_sources()
    monthly_sales = apis.get_monthly_sales()
    top_selling_products = apis.top_selling_products() 
    data = {'active': 'home',
            'username': request.user,
            'sources': sources,
            'today_sales': data,
            'monthly_sales': monthly_sales,
            'top_selling_producs':top_selling_products
            }
    return render(request, 'home/home.html', context=data)

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
    analysis.analyis_monthly_sales(request)
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
            product_name__icontains=product_prefix)[:5]
        product_names = [[prdct.product_name, prdct.stock_quantity]
                         for prdct in found_products]
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
    username = request.GET.get('user')
    current_transaction_type = request.GET.get('current_transaction_type')
    print("------------------------------- )))))))))))))))))))))))))))))")
    print(current_transaction_type)
    print("------------------------------- )))))))))))))))))))))))))))))")
    final_items = []
    total_price = 0
    for key, _ in request.GET.items():
        if key.startswith('items['):
            indices = key[:-2].split('[')[1:3]  # Get the two indices
            if len(indices) == 2:  # Only process valid item keys
                item_values = request.GET.getlist(key)
                if item_values:
                    final_items.append({
                        'name': item_values[1],
                        'quantity': item_values[3],
                    })
                    # incrementing the quantity from database
                    curr_product = models.Product.objects.filter(
                        id=item_values[0]).first()
                    if curr_product:
                        # updating the stock in database
                        pass
                        if curr_product.stock_quantity-int(item_values[3]) >= 1:
                            curr_product.stock_quantity -= int(item_values[3])
                            curr_product.save()
                    total_price += int(item_values[2])
    current_transaction = models.Transactions.objects.create(
        total_amount=total_price, status=0,transaction_type=current_transaction_type)
    current_transaction.save()
    current_logedin_user = User.objects.filter(username=request.user).first()
    if current_logedin_user:
        sales_manager = models.Admin.objects.filter(
            user_id=current_logedin_user).first()
        tem_curr_user = User.objects.filter(username=username).first()
        curr_customer = models.Customer.objects.filter(
            user_id=tem_curr_user).first()
        place_item = models.Sales.objects.create(
            sales_manager_id=sales_manager,
            total_amount=total_price,
            user_id=curr_customer,
            transactions_id=current_transaction,
            items=final_items
        )
        place_item.save()

        if place_item:
            return redirect('home/entry')

    return JsonResponse({"data": [str(curr_customer)
                                  ], "message": 'no product'})


#Inventory Product 
@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')
        address = request.POST.get('address')
        username = name

        try:
            user = User.objects.create_user(username=username, password='defaultpassword')
            user.first_name = name
            user.save()

            # Create the customer
            customer = models.Customer.objects.create(user_id=user, customer_name=name, phone_number=number, address=address)
            return JsonResponse({'success': True, 'user': {'id': customer.id, 'name': name, 'number': number, 'address': address}})
        
        except Exception:
            return JsonResponse({'success': False ,'message':'Dublicate user name'})
        
    return JsonResponse({'success': False ,'message':'Error adding the user'})

@login_required
def get_customer(request):
    username = request.GET.get('username')
    user_id = request.GET.get('user_id')

    if username:
        customers = models.Customer.objects.filter(user_id__username__icontains=username)[:5]
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
            customer = models.Customer.objects.get(id=user_id)
            data = {
                'id': customer.id,
                'name': customer.customer_name,
                'address': customer.address,
                'phone': customer.phone_number,
            }
            return JsonResponse({'success': True, 'data': data})
        except models.Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})

    return JsonResponse({'success': False, 'error': 'No valid parameters provided'})

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        # expire_date = request.POST.get('expire_date')
        stock_quantity = int(request.POST.get('quantity'))
        category_id = request.POST.get('category')

        category = models.Categories.objects.get(id=category_id)
        product, created = models.Product.objects.get_or_create(
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
    categories = models.Categories.objects.all()
    return render(request, 'inventory.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = models.Categories.objects.create(categorie_name=name)
        return JsonResponse({'success': True, 'category': {'id': category.id, 'name': name}})
    return JsonResponse({'success': False})