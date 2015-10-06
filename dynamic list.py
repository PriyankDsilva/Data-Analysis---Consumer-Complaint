import pandas as pd
from datetime import *
import numpy as np
df=pd.read_csv('Other financial services.csv',low_memory=False)
df['Date received'] = pd.to_datetime(df['Date received'])
df['Date sent to company'] = pd.to_datetime(df['Date sent to company'])


YearList=pd.unique(df['Date received'].dt.year)
ProductList=pd.unique(df.Product)
CompanyList=pd.unique(df.Company)
StateList=pd.unique(df.State)

YearList=[2014]
CompanyList=['Wells Fargo']
StateList=['NJ']
print('YearList :',YearList)
print('ProductList :',ProductList)
print('CompanyList :',CompanyList)
print('StateList :',StateList)

FilteredDF=df[ (df['Date received'].dt.year.isin(YearList)) &
          (df['Product'].isin(ProductList)) &
          (df['Company'].isin(CompanyList)) &
          (df['State'].isin(StateList)) ]

print(FilteredDF)
