from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
            found_products = models.Product.objects.filter( product_name=prouct_name).first()
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
