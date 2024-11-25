import pandas as pd
from datetime import datetime
from . import models
from django.http import JsonResponse
import os
import json


def analyis_monthly_sales(request):
   
    current_year = datetime.now().year -2

    # Define date range for current year
    year_start_date = datetime(current_year, 1, 1)
    year_end_date = datetime(current_year, 12, 31, 23, 59, 59)

    # Filter sales for current year
    sales_this_year = models.Sales.objects.filter(
        date_time__range=(year_start_date, year_end_date)
    ).select_related('sales_manager', 'user').values(
        'id', 'date_time', 'items',
         'sales_manager_id__admin_name',
         'user_id__customer_name',
         'transactions_id__total_amount'
    )
    
    # Create DataFrame
    df = pd.DataFrame(list(sales_this_year))
    
    # Ensure items column is parsed from string to list
    def parse_items(x):
        if isinstance(x, str):
            try:
                return json.loads(x.replace("'", '"').replace('"[', '[').replace(']"', ']'))
            except json.JSONDecodeError:
                return []
        return x
    df['items'] = df['items'].apply(parse_items)

    # Explode the items column to create separate rows for each item
    df = df.explode('items')

    # Extract item details from the dictionary, handling non-dictionary items
    df['name'] = df['items'].apply(lambda x: x['name'] if isinstance(x, dict) else None)
    df['quantity'] = df['items'].apply(lambda x: x['quantity'] if isinstance(x, dict) else 0)

    # Drop the original items column
    df = df.drop('items', axis=1)
 
    # Save CSV to static/analysis folder
    static_path = os.path.join('static', 'analysis')
    if not os.path.exists(static_path):
        os.makedirs(static_path)
    csv_path = os.path.join(static_path, f"sales_data_{current_year}.csv")
    df.to_csv(csv_path)

    return JsonResponse({'data': f"{df.to_dict()}"})


