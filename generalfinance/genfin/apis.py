from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from . import models
import datetime
from colorama import Fore, Style
from django.db import connection
from django.conf import settings


def log(message):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def get_today_sales_data():
    try:
        today = datetime.datetime.now().date()
        start_date = datetime.datetime.combine(today, datetime.time.min)
        end_date = datetime.datetime.combine(today, datetime.time.max)

        today_sales = models.Sales.objects.filter(
            date_time__range=(start_date, end_date))
        today_transaction = models.Transactions.objects.filter(
            transaction_date__range=(start_date, end_date))
        today_sales_cash = sum(
            today.total_amount for today in today_transaction)

        item_sell = 0
        for sale in today_sales:
            for item in sale.items:
                item_sell = item_sell + int(item['quantity'])

        today_loans_transaction = models.Transactions.objects.filter(
            transaction_date__range=(start_date, end_date), transaction_type='loan')
        loans = sum(l_today.total_amount for l_today in today_loans_transaction)
    except Exception as e:
        # print(e)
        today_sales_cash = 0
        item_sell = 0
        loans = 0
    return {
        'total_sales_today': today_sales_cash,
        'today_sales_cash': max(loans, today_sales_cash) - min(loans, today_sales_cash),
        'total_items': item_sell,
        'total_loans_today': loans
    }


def get_today_payement_sources():
    today = datetime.datetime.now().date()
    start_date = datetime.datetime.combine(today, datetime.time.min)
    end_date = datetime.datetime.combine(today, datetime.time.max)

    try:
        today_transactions = models.Transactions.objects.filter(
            transaction_date__range=(start_date, end_date))

        sources_with_counts = {
            'Cash': 0,
            'Online': 0,
            'Loan': 0
        }

        for transaction in today_transactions:
            transaction_type = transaction.transaction_type
            if transaction_type in sources_with_counts:
                sources_with_counts[transaction_type] += 1

    except Exception as e:
        sources_with_counts = {'Cash': 0, 'Online': 0, 'Loan': 0}

    return {
        'Cash': sources_with_counts['Cash'],
        'Online': sources_with_counts['Online'],
        'Loan': sources_with_counts['Loan'],
    }


def get_monthly_sales():
    try:
        current_year = datetime.datetime.now().year
        monthly_sales = []

        for month in range(1, 13):
            start_date = datetime.datetime(current_year, month, 1)
            end_date = (start_date.replace(month=month+1, day=1) - datetime.timedelta(days=1)) \
                if month < 12 else datetime.datetime(current_year, 12, 31, 23, 59, 59)

            transactions = models.Transactions.objects.filter(
                transaction_date__range=(start_date, end_date))

            total_sales = sum(trans.total_amount for trans in transactions)
            monthly_sales.append(total_sales)
    except Exception as e:
        monthly_sales = [0]*12
    return monthly_sales


def top_selling_products():
    try:
        today = datetime.datetime.now().date()
        start_date = datetime.datetime.combine(today, datetime.time.min)
        end_date = datetime.datetime.combine(today, datetime.time.max)

        today_sales = models.Sales.objects.filter(
            date_time__range=(start_date, end_date))

        product_sales = {}
        for sale in today_sales:
            for item in sale.items:
                name = item['name']
                quantity = int(item['quantity'])
                if name in product_sales:
                    product_sales[name] += quantity
                else:
                    product_sales[name] = quantity

        sorted_products = sorted(product_sales.items(),
                                 key=lambda x: x[1], reverse=True)
        top_products = sorted_products[:5]  # Changed from 4 to 5

        labels = str([str(product[0])[:len(str(product[0]))//2]
                     for product in top_products]).replace("'", '"')
        labels = ''.join(
            char for char in labels if char.isalpha() or char in '[]," ')
        values = [product[1] for product in top_products]
    except Exception as e:
        labels = []
        values = []
    return {'error': 'dsfasd', 'labels': labels, 'values': values}


def default_payement_source():
    return 'Cash'


# ----------------------------------- Entry  ----------------------------------------------------------------------

@login_required
def get_user(request):
    # username_prefix = "s"/
    username_prefix = request.GET["username"]
    customer_names = []
    try:
        if username_prefix:
            customers = models.Customer.objects.filter(
                customer_name__startswith=username_prefix)[:4]
            customer_names = [[c.customer_name, f"{
                c.phone_number}"] for c in customers]
            # log(customer_names)
    except Exception as e:
        log(e)
        pass
    return JsonResponse({"data": customer_names})


@login_required
def get_product(request):
    product_prefix = request.GET["product"]
    product_names = []
    try:
        if product_prefix:
            found_products = models.Product.objects.filter(
                product_name__icontains=product_prefix)[:7]
            product_names = [[p.product_name, p.stock_quantity, p.price]
                             for p in found_products]
            log(product_names)
    except Exception as e:
        log(e)

    return JsonResponse({"data": product_names})


@login_required
def get_product_info(request):
    prouct_name = request.GET["product"]
    data = {'id': '', 'name': '', 'price': '', 'quantity': ''}
    if prouct_name:
        try:
            found_products = models.Product.objects.filter(
                product_name=prouct_name).first()
            if found_products:
                if int(str(found_products.stock_quantity)) >= 1:
                    data['id'] = found_products.pk
                    data['name'] = found_products.product_name
                    data['price'] = found_products.price
                    data['quantity'] = found_products.stock_quantity
                else:
                    data['quantity'] = -1
        except Exception as e:
            log(e)
    else:
        pass
    return JsonResponse({"data": data})


@login_required
def order_entry(request):
    if request.method == 'POST':
        curr_user = request.POST.get('orderby')
        order_user = str(curr_user).strip()

        order_items = request.POST.get('items')
        order_payement_type = request.POST.get('current_transaction_type')

        log(order_user)
        log(order_items)
        log(order_payement_type)

        final_items = []
        total_price = 0
        try:
            data = eval(str(order_items))  # Convert string to dictionary
            for item_key, item_data in data.items():
                final_items.append({
                    'name': item_data['name'],
                    'quantity': item_data['quantity']
                })
                total_price += item_data['price'] * item_data['quantity']
        except Exception as e:
            log(f"Error parsing order items: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unknown Error'})

        try:

            temp_customer = User.objects.filter(username=order_user).first()
            curr_customer = models.Customer.objects.filter(
                user_id=temp_customer).first()

            if not curr_customer:
                return JsonResponse({'status': 'failed', 'message': 'unknown user order'})

            temp_sales = User.objects.filter(username=request.user).first()
            current_sales_man = models.Admin.objects.filter(
                user_id=temp_sales).first()  # sales man

            if not curr_customer:
                return JsonResponse({'status': 'failed', 'message': 'unknown salesman loged in '})

            # if found a correct user and salesman then continue placing the order

            current_transaction = models.Transactions.objects.create(
                total_amount=total_price, status=0,
                transaction_type=order_payement_type)
            current_transaction.save()

            if not current_transaction:
                return JsonResponse({'status': 'failed', 'message': 'Error with the Transaction'})

            place_item = models.Sales.objects.create(
                sales_manager_id=current_sales_man,
                total_amount=total_price,
                user_id=curr_customer,
                transactions_id=current_transaction,
                items=final_items
            )
            if not place_item:
                current_transaction.delete()
                return JsonResponse({'status': 'failed', 'message': 'Error in order placement'})

            place_item.save()

            for item in final_items:
                try:
                    curr_prod = models.Product.objects.filter(
                        product_name=item['name']).first()
                    if curr_prod and curr_prod.stock_quantity >= int(item['quantity']):
                        curr_prod.stock_quantity = curr_prod.stock_quantity - \
                            int(item['quantity'])
                        curr_prod.save()
                except Exception as e:
                    log(f'error in {item}')
                    pass

        except Exception as e:
            log(f"Error processing order: {e}")
            return JsonResponse({'status': 'error', 'message': 'Unknown Error'})

        log('order places sucesfully')
        return JsonResponse({'status': 'success', 'message': 'Sucesfull placed the order'})


@login_required
def check_db_status(request):
    try:
        # Get database size based on database backend
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT pg_database_size(current_database())")
            elif connection.vendor == 'mysql':
                cursor.execute(
                    "SELECT SUM(data_length + index_length) FROM information_schema.tables WHERE table_schema = DATABASE()")
            else:
                cursor.execute("SELECT 0")  # Fallback for other databases
            db_size = cursor.fetchone()[0] or 0
            db_size_mb = round(db_size / (1024 * 1024), 2)

        status_info = {
            'status': 'ok',
            'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database_size_mb': db_size_mb,
            # 'total_records': {
            #     'sales': models.Sales.objects.count(),
            #     'products': models.Product.objects.count(),
            #     'transactions': models.Transactions.objects.count(),
            # },
            # 'system_info': {
            #     # 'memory_used_percent': memory.percent,
            #     # 'disk_used_percent': disk.percent,
            # }
        }
    except Exception as e:
        status_info = {
            'status': 'error',
            'message': str(e)
        }

    return JsonResponse(status_info)


@login_required
def get_all_products(request):
    try:
        page = int(request.GET.get('p_page', 1))
        items_per_page = 12
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        products = models.Product.objects.all()[start_idx:end_idx]
        total_products = models.Product.objects.count()

        product_data = [{
            'index': start_idx + idx + 1,
            'id': p.categorie_id,
            'name': p.product_name,
            'price': p.price,
            'quantity': p.stock_quantity,
            'quality': p.quality,
            'category': p.categorie_id.categorie_name,
        } for idx, p in enumerate(products)]

        return {
            'products': product_data,
            'total_pages': (total_products + items_per_page - 1) // items_per_page,
            'current_page_products': page
        }

    except Exception as e:
        return {
            'products': [],
            'total_pages': 0,
            'current_page_products': page
        }


def get_all_Categories(request):
    try:
        page = int(request.GET.get('c_page', 1))
        items_per_page = 13
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        categories = models.Categories.objects.all()[start_idx:end_idx]
        total_categories = models.Categories.objects.count()

        category_data = [{
            'index': start_idx + idx + 1,
            'id': c.id,
            'name': c.categorie_name
        } for idx, c in enumerate(categories)]

        return {
            'categories': category_data,
            'total_pages': (total_categories + items_per_page - 1) // items_per_page,
            'current_page_categories': page
        }
    except Exception as e:
        return {
            'categories': [],
            'total_pages': 0,
            'current_page_categories': page
        }
