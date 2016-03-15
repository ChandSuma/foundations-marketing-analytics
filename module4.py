# __________________________________________________________
# //////////////////////////////////////////////////////////
#
#    MODULE 4 - CUSTOMER LIFETIME VALUE
# __________________________________________________________
# //////////////////////////////////////////////////////////
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandasql import sqldf


# --- SEGMENT CUSTOMERS IN 2014 AND 2015 -------------------


# Load text file into local variable called 'data'
data = pd.read_table('purchases.txt', header = None)

# Add headers and interpret the last column as a date, extract year of purchase
data.columns = ['customer_id', 'purchase_amount', 'date_of_purchase']
data['date_of_purchase'] = pd.to_datetime(data.date_of_purchase)
data['year_of_purchase'] = pd.DatetimeIndex(data['date_of_purchase']).year
data['days_since'] = (pd.Timestamp('2016-01-01') - data['date_of_purchase']).dt.days

# Invoke library to compute key marketing indicators using SQL language

# Segment customers in 2015
customers_2015 = sqldf("SELECT customer_id, MIN(days_since) AS 'recency', MAX(days_since) AS 'first_purchase', COUNT(*) AS 'frequency', AVG(purchase_amount) AS 'amount' FROM data GROUP BY 1", globals())

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

customers_2015.segment = customers_2015.segment.astype('category').cat.reorder_categories(['inactive', 'cold', 'warm high value', 'warm low value', 'new warm', 'active high value', 'active low value', 'new active'], ordered=True)


# Segment customers in 2014
customers_2014 = sqldf("SELECT customer_id, MIN(days_since) - 365 AS 'recency', MAX(days_since) - 365 AS 'first_purchase', COUNT(*) AS 'frequency', AVG(purchase_amount) AS 'amount' FROM data WHERE days_since > 365 GROUP BY 1", globals())

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

customers_2014.segment = customers_2014.segment.astype('category').cat.reorder_categories(['inactive', 'cold', 'warm high value', 'warm low value', 'new warm', 'active high value', 'active low value', 'new active'], ordered=True)


# --- COMPUTE TRANSITION MATRIX ----------------------------


# Compute transition matrix
new_data = pd.merge(customers_2014, customers_2015, on='customer_id', how='left')
new_data.head()

transition = pd.crosstab(new_data.segment_x, new_data.segment_y)
print(transition)
# I don't know how to get the col/row name order right...

# Divide each row by its sum
transition = transition.apply(lambda r: r/r.sum(), axis=1)
print(transition)


# --- USE TRANSITION MATRIX TO MAKE PREDICTIONS ------------


# Initialize a matrix with the number of customers in each segment today and after 10 periods
segments = numpy.zeros(shape=(8,11))
segments[:, 0] = customers_2015.segment.value_counts(sort=False)
segments = pd.DataFrame(segments, columns=arange(2015,2026), index=customers_2015.segment.values.categories)
print(segments)

# Compute for each an every period
for i in range(2016, 2026):
    segments[i] = segments[i-1].dot(transition)
    segments[i] = segments[i].fillna(0)


# Plot inactive, active high value customers over time
segments.iloc[0].plot(kind='bar')
segments.iloc[].plot(kind='bar')

# Display how segments will evolve over time
print(segments.round(0))


# --- COMPUTE THE (DISCOUNTED) CLV OF A DATABASE -----------


# Yearly revenue per segment
# This comes directly from module 2, lines 160-161
yearly_revenue = pd.Series([0, 0, 0, 0, 0, 323.57, 52.31, 79.17], index=customers_2015.segment.values.categories)

# Compute revenue per segment
revenue_per_segment = segments.multiply(yearly_revenue, axis='index')
print(revenue_per_segment)

# Compute yearly revenue
yearly_revenue = revenue_per_segment.sum(axis=0)
print(yearly_revenue.round(0))
yearly_revenue.plot(kind='bar')

# Compute cumulated revenue
cumulated_revenue = yearly_revenue.cumsum(axis=0)
print(cumulated_revenue.round(0))
cumulated_revenue.plot(kind='bar')

# Create a discount factor
discount_rate = 0.10
discount = 1 / ((1 + discount_rate) ** np.arange(0,11))
print(discount)

# Compute discounted yearly revenue
disc_yearly_revenue = yearly_revenue.multiply(discount)
print(disc_yearly_revenue.round(0))
ax1 = disc_yearly_revenue.plot(kind='bar')
ax2 = ax1.twiny()
yearly_revenue.plot(kind='line', ax=ax2)

# Compute discounted cumulated revenue
disc_cumulated_revenue = disc_yearly_revenue.cumsum(axis=0)
print(disc_cumulated_revenue.round(0))
disc_cumulated_revenue.plot(kind='bar')

# What is the database worth?
print(disc_cumulated_revenue[2025] - yearly_revenue[2015])
