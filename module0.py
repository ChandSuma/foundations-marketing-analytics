
# __________________________________________________________
# //////////////////////////////////////////////////////////
#
#    MODULE 0 - INTRODUCTION
# __________________________________________________________
# //////////////////////////////////////////////////////////

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandasql import sqldf


# --- EXPLORE THE DATA -------------------------------------


# Load text file into local variable called 'data'
data = pd.read_table('purchases.txt', header = None)

# Display what has been loaded
data.head()
data.describe()

# Add headers and interpret the last column as a date, extract year of purchase
data.columns = ['customer_id', 'purchase_amount', 'date_of_purchase']
data['date_of_purchase'] = pd.to_datetime(data.date_of_purchase)
data['year_of_purchase'] = pd.DatetimeIndex(data['date_of_purchase']).year

# Display the data set after transformation
data.head()
data.describe()

# Explore the data using simple SQL statements

# Number of purchases per year
x = sqldf("SELECT year_of_purchase, COUNT(year_of_purchase) AS 'counter' FROM data GROUP BY 1 ORDER BY 1", globals())
x.plot(x=x.year_of_purchase, y='counter', kind='bar')

# Average purchase amount per year
x = sqldf("SELECT year_of_purchase, AVG(purchase_amount) AS 'avg_amount' FROM data GROUP BY 1 ORDER BY 1", globals())
x.plot(x=x.year_of_purchase, y='avg_amount', kind='bar')

# Total purchase amounts per year
x = sqldf("SELECT year_of_purchase, SUM(purchase_amount) AS 'sum_amount' FROM data GROUP BY 1 ORDER BY 1", globals())
x.plot(x=x.year_of_purchase, y='sum_amount', kind='bar')

# All in one
x = sqldf("SELECT year_of_purchase, COUNT(year_of_purchase) AS 'counter', AVG(purchase_amount) AS 'avg_amount', SUM(purchase_amount) AS 'sum_amount' FROM data GROUP BY 1 ORDER BY 1", globals())
print(x)
