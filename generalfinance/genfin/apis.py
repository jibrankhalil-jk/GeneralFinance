from django.contrib.auth.decorators import login_required
from . import models
import datetime
import pandas as pd


def get_today_sales_data():
    try:
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
    today_transaction = models.Transactions.objects.filter(transaction_date__range=(start_date, end_date))
    df = pd.DataFrame(list(today_transaction.values()))
    try:
        
        df_grouped = df.groupby('transaction_type').size().reset_index(name='count')
        sources_with_counts = dict(zip(df_grouped['transaction_type'], df_grouped['count']))
        
    except Exception as e:
        sources_with_counts = {'Cash': 0, 'online': 0, 'loan': 0}
    return {
        'Cash': sources_with_counts.get('Cash', 0),
        'Online': sources_with_counts.get('online', 0),
        'Loan': sources_with_counts.get('loan', 0),
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

        labels = str([product[0] for product in top_products]).replace("'", '"')
        values = [product[1] for product in top_products]
    except Exception as e:
        labels = []
        values = []
    return {'labels': labels, 'values': values}
