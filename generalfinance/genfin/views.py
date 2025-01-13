import sys
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . import models, apis, analysis
from django.http import JsonResponse
from django.contrib.auth import authenticate
import datetime

from colorama import Fore, Style


def log(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def redirect_to_home(request):
    # if user is not signed in then redirect to login page
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('home')


# ----------------------------------- Home  ----------------------------------------------------------------------

@login_required
def Home(request):
    data = get_home_data(request)
    log(data)
    return render(request, 'home/home.html', context=data)


def get_home_data(request):
    data = {'active': 'home',
            'username': request.user,
            'sources': {'Cash': 0, 'Online': 0, 'Loan': 0},
            'today_sales': {'total_sales_today': 0, 'today_sales_cash': 0, 'total_items': 0, 'total_loans_today': 0},
            'monthly_sales': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'top_selling_producs': None
            }

    try:
        data['today_sales'] = apis.get_today_sales_data()
    except Exception:
        pass
    try:
        data['sources'] = apis.get_today_payement_sources()
    except Exception:
        pass
    try:
        data['monthly_sales'] = apis.get_monthly_sales()
    except Exception:
        pass
    try:
        data['top_selling_producs'] = apis.top_selling_products()
    except Exception:
        pass

    # log(data['today_sales'])
    # log(data['sources'])
    # log(data['monthly_sales'])
    # log(data['top_selling_producs'])

    return data

# ----------------------------------- Entry  ----------------------------------------------------------------------


@login_required
def Entry(request):
    data = get_entry_data()
    log(data)
    # apis.get_user()
    return render(request, 'home/entry.html', context=data)


def get_entry_data():
    data = apis.default_payement_source()
    default_source = {'Online': '', 'Loan': '', 'Cash': ''}

    if (data == 'Online'):
        default_source['Online'] = 'checked'
    elif (data == 'Loan'):
        default_source['Loan'] = 'checked'
    else:
        default_source['Cash'] = 'checked'

    return {'active': 'entry', 'default_source': default_source}

# ----------------------------------- Inventory  ----------------------------------------------------------------------


@login_required
def Inventory(request):
    data = get_inventory_data(request)
    return render(request, 'home/inventory.html', context=data)


def get_inventory_data(request):
    products = apis.get_all_products(request)
    categories = apis.get_all_Categories(request)
    total = apis.getTotalProdCatCount(request)
    data = {'active': 'inventory'} | total | products | categories
    return data


# ----------------------------------- Khata  ----------------------------------------------------------------------


@login_required
def Khata(request):

    data = get_khata_data(request)

    return render(request, 'home/khata.html', context=data)


def get_khata_data(request):
    
    data = {'active': 'khata'}
    return data

# ----------------------------------- Analysis  ----------------------------------------------------------------------


@login_required
def Analysis(request):
    data = {'active': 'analysis'}
    return render(request, 'home/analysis.html', context=data)

# ----------------------------------- Settings  ----------------------------------------------------------------------


@login_required
def Settings(request):
    data = {'active': 'settings'}
    return render(request, 'home/settings.html', context=data)


# ----------------------------------- Other  ----------------------------------------------------------------------


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

            current_transaction = models.Transactions.objects.create(
                total_amount=total, status=0, transaction_date=date, transaction_type=tn_type)
            current_transaction.save()

            c_user = models.Customer.objects.filter(id=user_id[0]).first()
            if c_user:
                sale = models.Sales.objects.create(user_id=c_user, date_time=date, items=items,
                                                   sales_manager_id=sales_manager, total_amount=total, transactions_id=current_transaction)
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


def custom_404_view(request):
    return render(request, '404.html')

# -------------------------------------- Request views --------------------------------------


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


# Inventory Product


@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')
        address = request.POST.get('address')
        username = name

        try:
            user = User.objects.create_user(
                username=username, password='defaultpassword')
            user.first_name = name
            user.save()

            # Create the customer
            customer = models.Customer.objects.create(
                user_id=user, customer_name=name, phone_number=number, address=address)
            return JsonResponse({'success': True, 'user': {'id': customer.id, 'name': name, 'number': number, 'address': address}})

        except Exception:
            return JsonResponse({'success': False, 'message': 'Dublicate user name'})

    return JsonResponse({'success': False, 'message': 'Error adding the user'})


@login_required
def get_customer(request):
    username = request.GET.get('username')
    user_id = request.GET.get('user_id')

    if username:
        customers = models.Customer.objects.filter(
            user_id__username__icontains=username)[:5]
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
