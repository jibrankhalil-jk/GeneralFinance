import pandas as pd
from datetime import datetime
from . import models
from django.http import JsonResponse


def get_sales_of_month(_):
    # Define the date range for January 2021
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2021, 1, 31, 23, 59, 59)

    # Filter the Sales model based on the date range
    sales_in_january = models.Sales.objects.filter(date_time__range=(start_date, end_date))

    df = pd.DataFrame(list(sales_in_january.values()))
    print(df.head(12))
    
    return JsonResponse({'data': f"{df.to_dict()}"})