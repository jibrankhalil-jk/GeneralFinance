import json
import matplotlib.pyplot as plt
import os
from django.http import JsonResponse
import pandas as pd
from datetime import datetime
from . import models
import numpy as np
import matplotlib
matplotlib.use('Agg')


def analyis_monthly_sales(request):
    for y in range(0, 4):
        current_year = datetime.now().year - y
        year_start_date = datetime(current_year, 1, 1)
        year_end_date = datetime(current_year, 12, 31, 23, 59, 59)

        sales_this_year = models.Sales.objects.filter(
            date_time__range=(year_start_date, year_end_date)
        ).select_related('sales_manager', 'user').values(
            'id', 'date_time', 'items',
            'sales_manager_id__admin_name',
            'user_id__customer_name',
            'transactions_id__total_amount',
            'transactions_id__transaction_type'
        )

        df = pd.DataFrame(list(sales_this_year))

        def parse_items(x):
            if isinstance(x, str):
                try:
                    return json.loads(x.replace("'", '"').replace('"[', '[').replace(']"', ']'))
                except json.JSONDecodeError:
                    return []
            return x
        df['items'] = df['items'].apply(parse_items)

        df = df.explode('items')

        df['name'] = df['items'].apply(
            lambda x: x['name'] if isinstance(x, dict) else None)
        df['quantity'] = df['items'].apply(
            lambda x: x['quantity'] if isinstance(x, dict) else 0)

        df = df.drop('items', axis=1)

        static_path = os.path.join('static', 'analysis')
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        csv_path = os.path.join(static_path, f"sales_data_{current_year}.csv")
        df.to_csv(csv_path)

    products = models.Product.objects.all().select_related('product_name', 'price', 'cost_price').values(
        'product_name', 'price', 'cost_price',
        'categorie_id__categorie_name'
    )
    products_df = pd.DataFrame(list(products))
    products_df = products_df.rename(columns={'product_name': 'name'})
    products_df = products_df.rename(
        columns={'categorie_id__categorie_name': 'Category'})
    products_df = products_df.rename(columns={'cost_price': 'Sale Price'})
    products_csv_path = os.path.join(f"static/Products.csv")
    products_df.to_csv(products_csv_path)
    try:
        analysis_generator()
    except NameError:
        pass
    return JsonResponse({'data': f"{df.to_dict()}"})


def analysis_generator():

    files = os.listdir('static/analysis')

    csv_files = [file for file in files if file.endswith('.csv')]

    combined_df = pd.concat(
        [pd.read_csv(f'static/analysis/{file}') for file in csv_files], ignore_index=True)

    combined_df
    DF_2021_2024 = pd.DataFrame(combined_df)

    DF_2021_2024['date_time'] = pd.to_datetime(DF_2021_2024['date_time'])
    DF_2021_2024
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    for i in range(2021, 2025):
        temp_df = DF_2021_2024[DF_2021_2024['date_time'].dt.year == i]
        Sold_product_quantity = np.array([])
        for j in range(1, 13):
            Sold_product_quantity = np.append(Sold_product_quantity, len(
                temp_df[temp_df['date_time'].dt.month == j]))

        plt.figure(figsize=(15, 6))

        plt.plot(months, Sold_product_quantity)
        plt.xlabel('Months')
        plt.ylabel('Number of products sold')
        plt.title(f'Number of products sold monthwise in{i}')

    Unique_products = pd.DataFrame()
    Unique_products['name'] = DF_2021_2024['name'].unique()
    Unique_products['date time'] = 0

    Main_data = pd.read_csv('static/Products.csv')
    Main_data = pd.DataFrame(Main_data)
    Main_data['name'] = Main_data['name'].str.strip()
    Main_data['name'] = Main_data['name'].str.lower()

    Main_data = Main_data[pd.to_numeric(
        Main_data['name'], errors='coerce').isna()]
    Main_data = Main_data[Main_data['Sale Price'] > 1]
    Main_data = Main_data[Main_data['Category'] != 'All / Old Code']
    Main_data = Main_data[Main_data['Category'] != 'All']

    Merged_data = pd.merge(DF_2021_2024, Main_data, on="name")

    def assign_profit_margin(price):
        if price <= 100:
            return 0.05
        elif 100 < price <= 500:
            return 0.10
        elif 500 < price <= 1000:
            return 0.15
        elif 1000 < price <= 5000:
            return 0.20
        elif 5000 < price <= 12000:
            return 0.30

    Merged_data['Profit Margin'] = Merged_data['Sale Price'].apply(
        assign_profit_margin)

    Merged_data

    Merged_data['Cost Price'] = Merged_data['Sale Price'] * \
        (1 - Merged_data['Profit Margin'])
    Merged_data

    Merged_data['Cost Price'] = Merged_data['Sale Price'] * \
        (1 - Merged_data['Profit Margin'])
    Merged_data

    Merged_data['payment_method'] = np.random.choice(
        ['loan', 'cash', 'online'], size=len(Merged_data))
    Merged_data

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    for i in range(2021, 2025):
        temp_df = Merged_data[Merged_data['date_time'].dt.year == i]
        loan = len(temp_df[(temp_df['payment_method'] == 'loan') | (
            temp_df['payment_method'] == 'Loan')])
        cash = len(temp_df[(temp_df['payment_method'] == 'cash') | (
            temp_df['payment_method'] == 'Cash')])
        online = len(temp_df[(temp_df['payment_method'] == 'online') | (
            temp_df['payment_method'] == 'Online')])
        plt.figure(figsize=(8, 4))
        plt.bar(['loan', 'cash', 'online'], [loan, cash, online],
                color=['blue', 'green', 'red'])
        plt.xlabel('Payment Method')
        plt.ylabel('Number of Items')
        plt.title(f'Number of items purchased on loan, cash and online in{i}')
        plt.show()

    import csv
    Merged_data['Profit'] = Merged_data['Sale Price'] - \
        Merged_data['Cost Price']
    Merged_data
    Merged_data.to_csv('Merged_data.csv', index=False)

    summary_stats = Merged_data.describe()
    print(summary_stats)

    Merged_data['date_time'] = pd.to_datetime(
        Merged_data['date_time'], errors='coerce')
    print(Merged_data[Merged_data['date_time'].isnull()])

    sales_over_time = Merged_data.groupby(Merged_data['date_time'].dt.date)[
        'transactions_id__total_amount'].sum()

    plt.figure(figsize=(12, 6))
    sales_over_time.plot(kind='line')
    plt.title('Total Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Amount')
    plt.grid()
    plt.show()

    sales_by_customer = Merged_data.groupby('user_id__customer_name')[
        'transactions_id__total_amount'].sum().sort_values(ascending=False)

    plt.figure(figsize=(12, 6))
    sales_by_customer.plot(kind='bar')
    plt.title('Sales by Customer')
    plt.xlabel('Customer Name')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

    top_selling_products = Merged_data.groupby(
        'name')['quantity'].sum().sort_values(ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    top_selling_products.plot(kind='bar')
    plt.title('Top Selling Products')
    plt.xlabel('Product Name')
    plt.ylabel('Quantity Sold')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

    Merged_data['month'] = Merged_data['date_time'].dt.month
    Merged_data['day_of_week'] = Merged_data['date_time'].dt.day_name()

    monthly_sales = Merged_data.groupby(
        'month')['transactions_id__total_amount'].sum()

    plt.figure(figsize=(12, 6))
    monthly_sales.plot(kind='bar')
    plt.title('Monthly Sales')
    plt.xlabel('Month')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=0)
    plt.grid()
    plt.show()

    weekly_sales = Merged_data.groupby(
        'day_of_week')['transactions_id__total_amount'].sum()

    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_sales = weekly_sales.reindex(days_order)

    plt.figure(figsize=(12, 6))
    weekly_sales.plot(kind='bar', color='skyblue')
    plt.title('Weekly Sales')
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

    graphs_path = os.path.join('static', 'graphs')
    if not os.path.exists(graphs_path):
        os.makedirs(graphs_path)

    for i in range(2021, 2025):
        plt.figure(figsize=(15, 6))
        temp_df = DF_2021_2024[DF_2021_2024['date_time'].dt.year == i]
        Sold_product_quantity = [
            len(temp_df[temp_df['date_time'].dt.month == j]) for j in range(1, 13)]
        plt.plot(months, Sold_product_quantity)
        plt.xlabel('Months')
        plt.ylabel('Number of products sold')
        plt.title(f'Number of products sold monthwise in {i}')
        plt.savefig(os.path.join(
            graphs_path, f'monthly_sales_{i}.svg'), format='svg')
        plt.close()

    for i in range(2021, 2025):
        plt.figure(figsize=(8, 4))
        temp_df = Merged_data[Merged_data['date_time'].dt.year == i]
        payments = ['loan', 'cash', 'online']
        counts = [len(temp_df[temp_df['payment_method'] == p])
                  for p in payments]
        plt.bar(payments, counts, color=['blue', 'green', 'red'])
        plt.xlabel('Payment Method')
        plt.ylabel('Number of Items')
        plt.title(f'Payment Methods in {i}')
        plt.savefig(os.path.join(
            graphs_path, f'payment_methods_{i}.svg'), format='svg')
        plt.close()

    plt.figure(figsize=(12, 6))
    sales_over_time.plot(kind='line')
    plt.title('Total Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Amount')
    plt.grid()
    plt.savefig(os.path.join(graphs_path, 'sales_over_time.svg'), format='svg')
    plt.close()

    plt.figure(figsize=(12, 6))
    sales_by_customer.plot(kind='bar')
    plt.title('Sales by Customer')
    plt.xlabel('Customer Name')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)
    plt.grid()
    plt.savefig(os.path.join(
        graphs_path, 'sales_by_customer.svg'), format='svg')
    plt.close()

    plt.figure(figsize=(12, 6))
    top_selling_products.plot(kind='bar')
    plt.title('Top Selling Products')
    plt.xlabel('Product Name')
    plt.ylabel('Quantity Sold')
    plt.xticks(rotation=45)
    plt.grid()
    plt.savefig(os.path.join(graphs_path, 'top_products.svg'), format='svg')
    plt.close()

    Merged_data['month'] = Merged_data['date_time'].dt.month
    Merged_data['day_of_week'] = Merged_data['date_time'].dt.day_name()

    monthly_sales = Merged_data.groupby(
        'month')['transactions_id__total_amount'].sum()

    plt.figure(figsize=(12, 6))
    monthly_sales.plot(kind='bar')
    plt.title('Monthly Sales')
    plt.xlabel('Month')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=0)
    plt.grid()
    plt.savefig(os.path.join(graphs_path, 'Monthly_Sales.svg'), format='svg')
    plt.close()

    weekly_sales = Merged_data.groupby(
        'day_of_week')['transactions_id__total_amount'].sum()

    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_sales = weekly_sales.reindex(days_order)

    plt.figure(figsize=(12, 6))
    weekly_sales.plot(kind='bar', color='skyblue')
    plt.title('Weekly Sales')
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)
    plt.grid()
    plt.savefig(os.path.join(graphs_path, 'Weekly_Sales.svg'), format='svg')
    plt.close()

    Merged_data['year'] = pd.DatetimeIndex(Merged_data['date_time']).year
    Merged_data['month'] = pd.DatetimeIndex(Merged_data['date_time']).month

    Merged_data['total_sales'] = Merged_data['Sale Price'] * \
        Merged_data['quantity']
    Merged_data['total_cost'] = Merged_data['Cost Price'] * \
        Merged_data['quantity']
    Merged_data['profit'] = Merged_data['total_sales'] - \
        Merged_data['total_cost']

    monthly_summary = Merged_data.groupby(['year', 'month']).agg(
        total_profit=('profit', 'sum')
    ).reset_index()

    pivot_table = monthly_summary.pivot(
        index='month', columns='year', values='total_profit')

    plt.figure(figsize=(12, 6))
    pivot_table.plot(kind='bar')
    plt.title('Total Profit per Month for Each Year (2021 - 2024)')
    plt.xlabel('Month')
    plt.ylabel('Total Profit')
    plt.xticks(rotation=0)
    plt.legend(title='Year')
    plt.grid(axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(
        graphs_path, 'Total Profit per Month for Each Year (2021 - 2024).svg'), format='svg')
    plt.close()

    payment_method_distribution = Merged_data['payment_method'].value_counts()

    plt.figure(figsize=(8, 8))
    payment_method_distribution.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=[
                                     'skyblue', 'lightgreen', 'coral'])
    plt.title('Distribution of Sales by Payment Method')
    plt.ylabel('')
    plt.savefig(os.path.join(
        graphs_path, 'Distribution of Sales by Payment Method (2021 - 2024).svg'), format='svg')
    plt.close()
