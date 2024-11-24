from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from . import forms, models
from django.http import JsonResponse
from django.contrib.auth import authenticate
# from .models import User
from django.utils.crypto import get_random_string
import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use('Agg')
 
def get_today_sales_data():
    today = datetime.datetime.now().date()
    start_date = datetime.datetime.combine(today, datetime.time.min)
    end_date = datetime.datetime.combine(today, datetime.time.max)

    today_sales = models.Sales.objects.filter(date_time__range=(start_date, end_date))
    today_transaction = models.Transactions.objects.filter(transaction_date__range=(start_date, end_date))
    today_sales_cash = sum(today.total_amount for today in today_transaction)

    item_sell = 0
    for sale in today_sales:
        for item in sale.items :
           item_sell = item_sell + int(item['quantity'])
            
     
    today_loans_transaction = models.Transactions.objects.filter(transaction_date__range=(start_date, end_date),transaction_type='loan')
    loans = sum(l_today.total_amount for l_today in today_loans_transaction)

    return {
        'total_sales_today':today_sales_cash  ,
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
    df_grouped = df.groupby('transaction_type').size().reset_index(name='count')
    sources_with_counts = df_grouped.to_dict('records')
    labels = [item['transaction_type'] for item in sources_with_counts]
    data = [item['count'] for item in sources_with_counts]
    # Create a BytesIO buffer to store the SVG
  
    
    try:
        with io.BytesIO() as buffer:
            # Create and save the pie chart
            plt.clf()
            fig = plt.figure(figsize=(8, 6))
            if data and labels:
                plt.pie(data, labels=labels, autopct='%1.1f%%')
                plt.title('Payment Sources Distribution')
                
                # Save as SVG to the buffer
                plt.savefig(buffer, format='svg', bbox_inches='tight')
                plt.close(fig)
                
                # Get the SVG content from the buffer
                buffer.seek(0)
                svg_content = buffer.getvalue().decode('utf-8')
            else:
                svg_content = ''
    except Exception as e:
        print(f"Error generating chart: {e}")
        svg_content = ''
    
    return { 
        'chart_svg': svg_content
    }
    

@login_required
def get_all_the_products(request):
    pass