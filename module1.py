
# __________________________________________________________
# //////////////////////////////////////////////////////////
#
#    MODULE 1 - STATISTICAL SEGMENTATION
# __________________________________________________________
# //////////////////////////////////////////////////////////
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandasql import sqldf
from sklearn.preprocessing import scale
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree


# --- COMPUTING RECENCY, FREQUENCY, MONETARY VALUE ---------


# Load text file into local variable called 'data'
data = pd.read_table('purchases.txt', header = None)

# Add headers and interpret the last column as a date, extract year of purchase
data.columns = ['customer_id', 'purchase_amount', 'date_of_purchase']
data['date_of_purchase'] = pd.to_datetime(data.date_of_purchase)
data['days_since'] = (pd.Timestamp('2016-01-01') - data['date_of_purchase']).dt.days


# Display the data after transformation
data.head()
data.describe()

# Compute key marketing indicators using SQL language

# Compute recency, frequency, and average purchase amount
customers = sqldf("SELECT customer_id, MIN(days_since) AS 'recency', COUNT(*) AS 'frequency', AVG(purchase_amount) AS 'amount' FROM data GROUP BY 1", globals())

# Explore the data
customers.head()
customers.describe()
customers.recency.hist(bins=20)
customers.frequency.hist(bins=24)
customers.amount.hist()
customers.amount.hist(bins=99)


# --- PREPARING AND TRANSFORMING DATA ----------------------


# Copy customer data into new data frame
new_data = customers

# Remove customer id as a variable, store it as row names
new_data.head()
new_data = new_data.set_index(new_data.customer_id).iloc[:,1:4]
new_data.head()

# Take the log-transform of the amount, and plot
new_data.amount = log(new_data.amount)
new_data.amount.hist(bins=19)

# Standardize variables
new_data = pd.DataFrame(scale(new_data), index=new_data.index, columns=new_data.columns)
new_data.head()


# --- RUNNING A HIERARCHICAL SEGMENTATION ------------------


# Compute distance metrics on standardized data
# This will likely generate an error on most machines
# d = dist(new_data)

# Take a 10% sample
customers_sample = customers.iloc[::10, :]
new_data_sample  = new_data.iloc[::10, :]

# Compute distance metrics on standardized data
#d = pdist(new_data_sample)
#not needed for ward

# Perform hierarchical clustering on distance metrics
c = linkage(new_data_sample, method='ward')

# Plot the dendogram
dendrogram(c, get_leaves=True, labels=None)

# Cut at 9 segments
members = pd.DataFrame(cut_tree(c, n_clusters = 9), index=new_data_sample.index, columns=['ClusterNumber'])

# Show 30 first customers, frequency table
members.iloc[0:30]
members.ClusterNumber.value_counts(sort=False)

# Show profile of each segment
customers_sample_new = customers_sample.set_index(customers_sample.customer_id).iloc[:,1:4]
customers_sample_new.groupby(members.ClusterNumber).mean()
