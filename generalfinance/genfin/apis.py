from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from . import models
import datetime
from colorama import Fore, Style


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
    today_transaction = models.Transactions.objects.filter(
        transaction_date__range=(start_date, end_date))
    df = pd.DataFrame(list(today_transaction.values()))
    try:

        df_grouped = df.groupby(
            'transaction_type').size().reset_index(name='count')
        sources_with_counts = dict(
            zip(df_grouped['transaction_type'], df_grouped['count']))

    except Exception as e:
        sources_with_counts = {'Cash': 0, 'Online': 0, 'Loan': 0}
    return {
        'Cash': sources_with_counts['Cash'],
        'Online': sources_with_counts['Online'],
        'Loan': sources_with_counts['Loan'],
        # 'today_payement_sources': sources_with_counts
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
# def get_user():
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


# @login_required
# def order_entry(request):
#     log(request.method)
#     if request.method == 'POST':
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
