# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:21:03 2019

@author: movermye
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.linear_model import LinearRegression
import numpy as np
plt.close('all')


class SpendAnalysis():
    
    def __init__(self):
        ''' Create and format a Dataframe for chase credit card'''
        self.card_df = self.chase_csv_import("card-data")
        self.card_df['source'] = 'card'
        self.card_df['Date'] =pd.to_datetime(self.card_df['Post Date'])
        
        ''' Create and format a Dataframe for chase checking. This Dataframe is used
        to estimate cash flow out, so a balance column is created that has been
        corrected for anomalies'''
        self.checking_df = self.chase_csv_import("checking-data")
        self.checking_df['source'] = 'checking'
        self.checking_df['Date'] =pd.to_datetime(self.checking_df['Posting Date'])
        self.checking_df['epoch'] = (self.checking_df['Date'] - dt.datetime(1970,1,1)).dt.total_seconds()
        
        self.checking_df['days'] = (self.checking_df['epoch'] - self.checking_df['epoch'].min())/(3600 * 24)
        
        self.checking_df['epoch'] = self.checking_df['epoch'] - self.checking_df['epoch'].min()
        
        self.checking_df.sort_values(by=['Date'], inplace=True)
        self.checking_df['test_balance'] = self.checking_df.Amount.cumsum() + self.checking_df.Balance.values[0] + 2300
        select_crit = ((~self.checking_df.Description.str.contains('J&J')) &\
                       (~self.checking_df.Description.str.contains('Wealthfront')) &\
                       (~self.checking_df.Description.str.contains('Apex Clearing')) &\
                       (~self.checking_df.Description.str.contains('ATM CHECK DEPOSIT 04/19 9019 PLAINFIELD RD BLUE ASH OH')) &\
                       (~self.checking_df.Description.str.contains('Online Transfer to SAV')) &\
                       (~self.checking_df.Description.str.contains('TRANSFER TO SAV'))) 
        self.checking_df['select_balance'] = self.checking_df.where(select_crit).Amount.cumsum() + self.checking_df.Balance.values[0]
        
        ''' Create and formate Dataframe for Chase savings '''
        self.savings_df = self.chase_csv_import("savings-data")
        self.savings_df['source'] = 'savings'
        self.savings_df['Date'] =pd.to_datetime(self.savings_df['Posting Date'])
        
        # create and format the main df
        self.all_chase_df = pd.concat([self.card_df, self.checking_df, self.savings_df], 
               ignore_index=True, sort=True)

        self.all_chase_df.sort_values(by=['Date'], inplace=True)
        

    def chase_csv_import(self, path):
        # When pointed to a directory of chase bank csv export, this 
        # function creates a DataFrame with all the content. Because
        # duplicates are droped from combo_df, you should be able to 
        # drop csv exports in th efolder willy nilly, though this is
        # not tested
        csv_name_list = os.listdir(path)
        df_list = []
        
        for csv_name in csv_name_list:
            df = pd.read_csv(os.path.join(path, csv_name))
            df_list.append(df)
            
        combo_df = pd.concat(df_list, ignore_index=True)
        combo_df.drop_duplicates(inplace=True)
        combo_df['no_num_description'] = combo_df.Description.str.replace('\d+', '')
        
        return combo_df
  
    def raw_chase_plot(self):
        # plot the raw balances for chase related accounts 
        
        f,a = plt.subplots(1,1)
        f.suptitle('Summary of Chase accounts - raw')
        
        crit = self.all_chase_df.source.str.contains("checking")
        a.plot(self.all_chase_df.loc[crit].Date, 
               self.all_chase_df.loc[crit].Balance, 
               label='Checking Balance')
        
        crit = self.all_chase_df.source.str.contains("savings")
        a.plot(self.all_chase_df.loc[crit].Date, 
               self.all_chase_df.loc[crit].Balance, 
               label='Savings Balance')
        
        plt.plot(self.all_chase_df.loc[crit].Date, 
                 self.all_chase_df.loc[crit].Balance, 'g*')




'''
# high level stats
crit = (df['no_num_description'].str.lower().str.contains('itunes') &\
        df['no_num_description'].str.lower().str.contains('bill'))
itunes_spend = df.loc[crit].Amount.sum()

crit = (df['no_num_description'].str.lower().str.contains('j&j'))
mark = df.loc[crit]



f,a = plt.subplots(1,1)
start_time = '2017-05-18'
X = checking_df.loc[checking_df.Date > start_time].Date
Y = checking_df.loc[checking_df.Date > start_time].select_balance

a.plot(checking_df.Date, checking_df.Balance, '+', label='Balance')
a.plot(checking_df.Date, checking_df.select_balance, 'o', label='Select Balance')
a.plot(checking_df.Date, checking_df.test_balance, '*', label='Test Balance')
a.plot(X, Y, '-', label='Select Balance barf')
a.legend()

f,a = plt.subplots(1,1)
start_time = '2017-05-18'
checking_df.dropna(subset=['epoch', 'select_balance'], inplace=True)
X = checking_df.loc[checking_df.Date > start_time].epoch
Y = checking_df.loc[checking_df.Date > start_time].select_balance
model = LinearRegression()
#model.fit(X,Y)
#Yhat = model.predict(X[:, np.newaxis])
z = np.polyfit(X, Y, 1)
p = np.poly1d(z)

a.plot(checking_df.epoch, checking_df.Balance, '+', label='Balance')
a.plot(checking_df.epoch, checking_df.select_balance, '-', label='Select Balance')
a.plot(X, Y, 'o', label='fit region')
a.plot(X, p(X), '--', label='fit')
a.plot(checking_df.epoch, checking_df.test_balance, '*', label='Test Balance')
#a.plot(X, Yhat, '-', label='Select Balance barf')

a.legend()

# create "spend/day" trendline
start_time = '2017-05-18' #after this day, data is clean
checking_df.dropna(subset=['epoch', 'select_balance'], inplace=True)
X = checking_df.loc[checking_df.Date > start_time].days
Y = checking_df.loc[checking_df.Date > start_time].select_balance
z = np.polyfit(X, Y, 1)
p = np.poly1d(z)

# plot balance with fit line
f,a = plt.subplots(1,1)
f.suptitle(f'Spend rate is ${abs(round(p[1],1))}/day')
a.plot(checking_df.days, checking_df.Balance, '+', label='Balance')
a.plot(checking_df.days, checking_df.select_balance, '-', label='Select Balance (no JnJ income or internal tnsf)')
a.plot(X, Y, 'o', label='fit region')
a.plot(X, p(X), '--', label='fit')
a.plot(checking_df.days, checking_df.test_balance, '*', label='Test Balance')
#a.plot(X, Yhat, '-', label='Select Balance barf')
a.legend()


#if __name__ == '__main__':
'''