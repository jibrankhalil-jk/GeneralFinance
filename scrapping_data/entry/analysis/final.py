import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import os

# List all files in the 'analysis' directory
files = os.listdir('analysis')

# Filter out the CSV files
csv_files = [file for file in files if file.endswith('.csv')]

# Read and concatenate all CSV files into a single DataFrame
combined_df = pd.concat([pd.read_csv(f'analysis/{file}') for file in csv_files], ignore_index=True)

# Display the combined DataFrame
combined_df
DF_2021_2024=pd.DataFrame(combined_df)

DF_2021_2024['date_time']=pd.to_datetime(DF_2021_2024['date_time'])
DF_2021_2024
months=['January','February','March','April','May','June','July','August','September','October','November','December']

#Loop for yearwise analysis of number of product sold in months
for i in range(2021,2025):
    temp_df=DF_2021_2024[DF_2021_2024['date_time'].dt.year==i]
    Sold_product_quantity=np.array([])
    for j in range(1,13):
        Sold_product_quantity=np.append(Sold_product_quantity,len(temp_df[temp_df['date_time'].dt.month == j]))
    #graph to show number of product sold monthwise
    plt.figure(figsize=(15,6))
    #in place of range put the name of the months
    plt.plot(months,Sold_product_quantity)
    plt.xlabel('Months')
    plt.ylabel('Number of products sold')
    plt.title(f'Number of products sold monthwise in{i}')
    
Unique_products=pd.DataFrame()
Unique_products['name']=DF_2021_2024['name'].unique()
Unique_products['date time']=0

Main_data=pd.read_csv('analysis/Products.csv')
Main_data=pd.DataFrame(Main_data)
Main_data['name']=Main_data['name'].str.strip()
Main_data['name'] = Main_data['name'].str.lower()

#Cleaning the Data by removing the product whos 
#Product name is invalid
#Sale price is invalid
#Category is invalid
Main_data=Main_data[pd.to_numeric(Main_data['name'], errors='coerce').isna()]
Main_data=Main_data[Main_data['Sale Price']>1]
Main_data=Main_data[Main_data['Category'] != 'All / Old Code']
Main_data=Main_data[Main_data['Category'] != 'All']

#If the both have the same product name then merge it and form new dataset
Merged_data=pd.merge(DF_2021_2024,Main_data,on="name")


#Remove the columns which are not required
Merged_data.drop(['sales_manager_id__admin_name'],axis=1,inplace=True)
Merged_data.drop(['id'],axis=1,inplace=True)
Merged_data.drop(['Unnamed: 0'],axis=1,inplace=True)


#we have to divide the product on the base of sale price range 
# print(Merged_data[Merged_data['Sale Price']==2])
# print(Merged_data['Sale Price'].max())
# print(Merged_data[Merged_data['Sale Price']==11898.0])


#Product whose sale price is between 1 to 100 their profit margin is 5%, make new column in the data frame
def assign_profit_margin(price):
    if price <= 100:
        return 0.05  # 5%
    elif 100 < price <= 500:
        return 0.10  # 10%
    elif 500 < price <= 1000:
        return 0.15  # 15%
    elif 1000 < price <= 5000:
        return 0.20  # 20%
    elif 5000 < price <= 12000:
        return 0.30  # 30%

# Apply the function to create a new 'Profit Margin' column
Merged_data['Profit Margin'] = Merged_data['Sale Price'].apply(assign_profit_margin)


#Product whose sale price is between 100 to 500 their profit margin is 10%
#Product whose sale price is between 500 to 1000 their profit margin is 15%
#Product whose sale price is between 1000 to 5000 their profit margin is 20%
#Product whose sale price is between 5000 to 12000 their profit margin is 30%

Merged_data

#Calculating cost price of each product 

Merged_data['Cost Price'] = Merged_data['Sale Price'] * (1 - Merged_data['Profit Margin'])
Merged_data


Merged_data['Cost Price'] = Merged_data['Sale Price'] * (1 - Merged_data['Profit Margin'])
Merged_data


#Add another column in which we have three different values loan, cash, online
Merged_data['payment_method']=np.random.choice(['loan', 'cash', 'online'], size=len(Merged_data))
Merged_data

#Yearwise how much items are purchased on loan, cash and online 
months=['January','February','March','April','May','June','July','August','September','October','November','December']

for i in range(2021,2025):
    temp_df=Merged_data[Merged_data['date_time'].dt.year==i]
    loan=len(temp_df[temp_df['payment_method'] == 'loan'])
    cash=len(temp_df[temp_df['payment_method'] == 'cash'])
    online=len(temp_df[temp_df['payment_method'] == 'online'])
    #Number of items purchased on loan, cash and online 
    plt.figure(figsize=(8,4))
    plt.bar(['loan','cash','online'],[loan,cash,online],color=['blue','green','red'])
    plt.xlabel('Payment Method')
    plt.ylabel('Number of Items')
    plt.title(f'Number of items purchased on loan, cash and online in{i}')
    plt.show()
        
    
#Profit from each product
import csv
Merged_data['Profit'] = Merged_data['Sale Price'] - Merged_data['Cost Price']
Merged_data
#Save the dataset
Merged_data.to_csv('Merged_data.csv', index=False)

# Summary statistics
summary_stats = Merged_data.describe() 
print(summary_stats) 

Merged_data['date_time'] = pd.to_datetime(Merged_data['date_time'], errors='coerce')

# Check for any rows that couldn't be converted
print(Merged_data[Merged_data['date_time'].isnull()])

sales_over_time = Merged_data.groupby(Merged_data['date_time'].dt.date)['transactions_id__total_amount'].sum()

plt.figure(figsize=(12, 6))
sales_over_time.plot(kind='line')
plt.title('Total Sales Over Time')
plt.xlabel('Date')
plt.ylabel('Total Amount')
plt.grid()
plt.show()


# Group by customer name and sum the total amount
sales_by_customer = Merged_data.groupby('user_id__customer_name')['transactions_id__total_amount'].sum().sort_values(ascending=False)

# Plotting
plt.figure(figsize=(12, 6))
sales_by_customer.plot(kind='bar')
plt.title('Sales by Customer')
plt.xlabel('Customer Name')
plt.ylabel('Total Amount')
plt.xticks(rotation=45)
plt.grid()
plt.show()


# Group by product name and sum the quantity
top_selling_products = Merged_data.groupby('name')['quantity'].sum().sort_values(ascending=False).head(10)

# Plotting
plt.figure(figsize=(12, 6))
top_selling_products.plot(kind='bar')
plt.title('Top Selling Products')
plt.xlabel('Product Name')
plt.ylabel('Quantity Sold')
plt.xticks(rotation=45)
plt.grid()
plt.show()


# Extract month and day of week
Merged_data['month'] = Merged_data['date_time'].dt.month
Merged_data['day_of_week'] = Merged_data['date_time'].dt.day_name()

# Group by month and sum the total amount
monthly_sales = Merged_data.groupby('month')['transactions_id__total_amount'].sum()

# Plotting monthly sales
plt.figure(figsize=(12, 6))
monthly_sales.plot(kind='bar')
plt.title('Monthly Sales')
plt.xlabel('Month')
plt.ylabel('Total Amount')
plt.xticks(rotation=0)
plt.grid()
plt.show()

# Group by day of week and sum the total amount
weekly_sales = Merged_data.groupby('day_of_week')['transactions_id__total_amount'].sum()

# Reorder days for plotting
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_sales = weekly_sales.reindex(days_order)



# Plotting weekly sales
plt.figure(figsize=(12, 6))
weekly_sales.plot(kind='bar', color='skyblue')
plt.title('Weekly Sales')
plt.xlabel('Day of the Week')
plt.ylabel('Total Amount')
plt.xticks(rotation=45)
plt.grid()
plt.show()