# __________________________________________________________
# //////////////////////////////////////////////////////////
#
#    MODULE 2 - MANAGERIAL SEGMENTATION
# __________________________________________________________
# //////////////////////////////////////////////////////////
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandasql import sqldf


# --- COMPUTING RECENCY, FREQUENCY, MONETARY VALUE ---------


# Load text file into local variable called 'data'
data = pd.read_table('purchases.txt', header = None)

# Add headers and interpret the last column as a date, extract year of purchase
data.columns = ['customer_id', 'purchase_amount', 'date_of_purchase']
data['date_of_purchase'] = pd.to_datetime(data.date_of_purchase)
data['year_of_purchase'] = pd.DatetimeIndex(data['date_of_purchase']).year
data['days_since'] = (pd.Timestamp('2016-01-01') - data['date_of_purchase']).dt.days

# Display the data after transformation
data.head()
data.describe()

# Compute key marketing indicators using SQL language

# Compute recency, frequency, and average purchase amount
customers_2015 = sqldf("SELECT customer_id, MIN(days_since) AS 'recency', MAX(days_since) AS 'first_purchase', COUNT(*) AS 'frequency', AVG(purchase_amount) AS 'amount' FROM data GROUP BY 1", globals())

# Explore the data
customers_2015.head()
customers_2015.describe()
customers_2015.recency.hist(bins=20)
customers_2015.frequency.hist(bins=24)
customers_2015.amount.hist()
customers_2015.amount.hist(bins=99)


# --- CODING A MANAGERIAL SEGMENTATION ---------------------


# Simple 2-segment solution based on recency alone
customers_2015['segment'] = np.where(customers_2015['recency']>=365*3, 'inactive', np.nan)  # or use 'NA' instead of np.nan
customers_2015.segment.value_counts(sort=False)  #table
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# A more complex 3-segment solution based on recency alone
customers_2015['segment'] = np.where(customers_2015['recency']>365*3, 'inactive', np.where(customers_2015['recency']>365*2, 'cold', np.nan))
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# Simple 2-segment solution using the which statement
customers_2015['segment']=np.empty(len(customers_2015), dtype=object)
customers_2015.segment.loc[customers_2015.recency>3*365] = 'inactive'
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# More complex 4-segment solution using which
customers_2015['segment']=np.empty(len(customers_2015), dtype=object)
customers_2015.segment.loc[customers_2015.recency>3*365] = 'inactive'
customers_2015.segment.loc[(customers_2015.recency<=3*365) & (customers_2015.recency>2*365)] = 'cold'
customers_2015.segment.loc[(customers_2015.recency<=2*365) & (customers_2015.recency>1*365)] = 'warm'
customers_2015.segment.loc[customers_2015.recency<1*365] = 'active'
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# Complete segment solution using which, and exploiting previous test as input
customers_2015['segment']=np.empty(len(customers_2015), dtype=object)
customers_2015.segment.loc[customers_2015.recency>3*365] = 'inactive'
customers_2015.segment.loc[(customers_2015.recency<=3*365) & (customers_2015.recency>2*365)] = 'cold'
customers_2015.segment.loc[(customers_2015.recency<=2*365) & (customers_2015.recency>1*365)] = 'warm'
customers_2015.segment.loc[customers_2015.recency<1*365] = 'active'
customers_2015.segment.loc[(customers_2015.segment=='warm') & (customers_2015.first_purchase<=2*365)] = 'new warm'
customers_2015.segment.loc[(customers_2015.segment=='warm') & (customers_2015.amount<100)] = 'warm low value'
customers_2015.segment.loc[(customers_2015.segment=='warm') & (customers_2015.amount>=100)] = 'warm high value'
customers_2015.segment.loc[(customers_2015.segment=='active') & (customers_2015.first_purchase<=365)] = 'new active'
customers_2015.segment.loc[(customers_2015.segment=='active') & (customers_2015.amount<100)] = 'active low value'
customers_2015.segment.loc[(customers_2015.segment=='active') & (customers_2015.amount>=100)] = 'active high value'
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# Re-order factor in a way that makes sense
customers_2015.segment = customers_2015.segment.astype('category').cat.reorder_categories(['inactive', 'cold', 'warm high value', 'warm low value', 'new warm', 'active high value', 'active low value', 'new active'], ordered=True)
x=customers_2015.iloc[:,1:5]
x.groupby(customers_2015.segment).mean()  #aggregate


# --- SEGMENTING A DATABASE RETROSPECTIVELY ----------------


# Compute key marketing indicators using SQL language

# Compute recency, frequency, and average purchase amount
customers_2014 = sqldf("SELECT customer_id, MIN(days_since) - 365 AS 'recency', MAX(days_since) - 365 AS 'first_purchase', COUNT(*) AS 'frequency', AVG(purchase_amount) AS 'amount' FROM data WHERE days_since > 365 GROUP BY 1", globals())


# Complete segment solution using which, and exploiting previous test as input
customers_2014['segment']=np.empty(len(customers_2014), dtype=object)
customers_2014.segment.loc[customers_2014.recency>3*365] = 'inactive'
customers_2014.segment.loc[(customers_2014.recency<=3*365) & (customers_2014.recency>2*365)] = 'cold'
customers_2014.segment.loc[(customers_2014.recency<=2*365) & (customers_2014.recency>1*365)] = 'warm'
customers_2014.segment.loc[customers_2014.recency<1*365] = 'active'
customers_2014.segment.loc[(customers_2014.segment=='warm') & (customers_2014.first_purchase<=2*365)] = 'new warm'
customers_2014.segment.loc[(customers_2014.segment=='warm') & (customers_2014.amount<100)] = 'warm low value'
customers_2014.segment.loc[(customers_2014.segment=='warm') & (customers_2014.amount>=100)] = 'warm high value'
customers_2014.segment.loc[(customers_2014.segment=='active') & (customers_2014.first_purchase<=365)] = 'new active'
customers_2014.segment.loc[(customers_2014.segment=='active') & (customers_2014.amount<100)] = 'active low value'
customers_2014.segment.loc[(customers_2014.segment=='active') & (customers_2014.amount>=100)] = 'active high value'
x=customers_2014.iloc[:,1:5]
x.groupby(customers_2014.segment).mean()  #aggregate

# Re-order factor in a way that makes sense
customers_2014.segment = customers_2014.segment.astype('category').cat.reorder_categories(['inactive', 'cold', 'warm high value', 'warm low value', 'new warm', 'active high value', 'active low value', 'new active'], ordered=True)
x=customers_2014.iloc[:,1:5]
x.groupby(customers_2014.segment).mean()  #aggregate

# Show segmentation results
y=customers_2014.segment.value_counts(sort=False)
y.plot(kind='pie', figsize=(6, 6))
x=customers_2014.iloc[:,1:5]
x.groupby(customers_2014.segment).mean()  #aggregate


# --- COMPUTING REVENUE GENERATION PER SEGMENT -------------


# Compute how much revenue is generated by segments
# Notice that people with no revenue in 2015 do NOT appear
revenue_2015 = sqldf("SELECT customer_id, SUM(purchase_amount) AS 'revenue_2015' FROM data WHERE year_of_purchase = 2015 GROUP BY 1", globals())
revenue_2015.describe()

# Merge 2015 customers and 2015 revenue (the wrong way)
actual = pd.merge(customers_2015, revenue_2015)

# Merge 2015 customers and 2015 revenue (correct)
actual = pd.merge(customers_2015, revenue_2015, how='left')
actual.revenue_2015 = actual.revenue_2015.replace(np.nan, 0)

# Show average revenue per customer and per segment
x=actual.revenue_2015
x.groupby(customers_2015.segment).mean()  #aggregate

# Merge 2014 customers and 2015 revenue (correct)
forward = pd.merge(customers_2014, revenue_2015, how='left')
forward.revenue_2015 = forward.revenue_2015.replace(np.nan, 0)

# Show average revenue per customer and per segment
x = forward.revenue_2015
r = x.groupby(customers_2014.segment).mean()  #aggregate

# Re-order and display results
r = r.sort_values(ascending=False)
print(r)
r.plot(kind='bar')
