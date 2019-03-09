# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:21:03 2019

@author: movermye
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
plt.close('all')

def chase_csv_import(path):
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
  


 
''' Create and format a Dataframe for chase credit card'''
card_df = chase_csv_import("card-data")
card_df['source'] = 'card'
card_df['Date'] =pd.to_datetime(card_df['Post Date'])

''' Create and format a Dataframe for chase checking. This Dataframe is used
    to estimate cash flow out, so a balance column is created that has been
    corrected for anomalies'''
checking_df = chase_csv_import("checking-data")
checking_df['source'] = 'checking'
checking_df['Date'] =pd.to_datetime(checking_df['Posting Date'])
checking_df.sort_values(by=['Date'], inplace=True)
checking_df['test_balance'] = checking_df.Amount.cumsum() + checking_df.Balance.values[0] + 2300
select_crit = ((~checking_df.Description.str.contains('J&J')) &\
               (~checking_df.Description.str.contains('Wealthfront')) &\
               (~checking_df.Description.str.contains('Apex Clearing')) &\
               (~checking_df.Description.str.contains('ATM CHECK DEPOSIT 04/19 9019 PLAINFIELD RD BLUE ASH OH')) &\
               (~checking_df.Description.str.contains('Online Transfer to SAV')) &\
               (~checking_df.Description.str.contains('TRANSFER TO SAV'))) 
checking_df['select_balance'] = checking_df.where(select_crit).Amount.cumsum() + checking_df.Balance.values[0]



savings_df = chase_csv_import("savings-data")
savings_df['source'] = 'savings'
savings_df['Date'] =pd.to_datetime(savings_df['Posting Date'])

# create and format the main df
df = pd.concat([card_df, checking_df, savings_df], 
               ignore_index=True, sort=True)

df.sort_values(by=['Date'], inplace=True)

# high level stats
crit = (df['no_num_description'].str.lower().str.contains('itunes') &\
        df['no_num_description'].str.lower().str.contains('bill'))
itunes_spend = df.loc[crit].Amount.sum()

crit = (df['no_num_description'].str.lower().str.contains('j&j'))
mark = df.loc[crit]

crit = df.source.str.contains("checking")
plt.plot(df.loc[crit].Date, df.loc[crit].Balance, 'r*')
crit = df.source.str.contains("savings")
plt.plot(df.loc[crit].Date, df.loc[crit].Balance, 'g*')

f,a = plt.subplots(1,1)
a.plot(checking_df.Date, checking_df.Balance, label='Balance')
a.plot(checking_df.Date, checking_df.select_balance, label='Select Balance')
a.plot(checking_df.Date, checking_df.test_balance, label='Test Balance')
a.legend()


