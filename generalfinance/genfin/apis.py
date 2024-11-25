from django.contrib.auth.decorators import login_required
from . import models
import datetime
import pandas as pd


def get_today_sales_data():
    today = datetime.datetime.now().date()
    start_date = datetime.datetime.combine(today, datetime.time.min)
    end_date = datetime.datetime.combine(today, datetime.time.max)

    today_sales = models.Sales.objects.filter(
        date_time__range=(start_date, end_date))
    today_transaction = models.Transactions.objects.filter(
        transaction_date__range=(start_date, end_date))
    today_sales_cash = sum(today.total_amount for today in today_transaction)

    item_sell = 0
    for sale in today_sales:
        for item in sale.items:
            item_sell = item_sell + int(item['quantity'])

    today_loans_transaction = models.Transactions.objects.filter(
        transaction_date__range=(start_date, end_date), transaction_type='loan')
    loans = sum(l_today.total_amount for l_today in today_loans_transaction)

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
    df_grouped = df.groupby(
        'transaction_type').size().reset_index(name='count')
    sources_with_counts = df_grouped.to_dict('records')
    # labels = [item['transaction_type'] for item in sources_with_counts]
    # data = [item['count'] for item in sources_with_counts]
    
    return {
        'cash':  sources_with_counts['Cash'],
        'online': sources_with_counts['online'],
        'loan':  sources_with_counts['loan'],
        # 'today_payement_sources': sources_with_counts
    }


def get_monthly_sales():
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

    return monthly_sales


def top_selling_products():
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

    labels = str([product[0] for product in top_products]).replace("'", '"')
    values = [product[1] for product in top_products]

    return {'labels': labels, 'values': values}
