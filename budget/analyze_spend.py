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
        
        self.fit_spend_rate()
        

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
        
    def fit_spend_rate(self):
        
        self.spend_is_clean_after_this = '2017-05-18' #after this day, data is clean
        no_nan_checking = self.checking_df.dropna(subset=['epoch', 'select_balance'])
        
        crit = (no_nan_checking.Date > self.spend_is_clean_after_this)
        self.spend_X = no_nan_checking.loc[crit].days
        self.spend_Y = no_nan_checking.loc[crit].select_balance
        
        spend_fit_coefficients = np.polyfit(self.spend_X, self.spend_Y, 1)
        self.spend_fit = np.poly1d(spend_fit_coefficients)
        self.spend_dollars_per_day = self.spend_fit[1]
    
    def fit_spend_plot(self):
        
        f,a = plt.subplots(1,1)
        f.suptitle(f'Spend rate is ${abs(round(self.spend_dollars_per_day, 2))}/day')
        a.plot(self.checking_df.days, self.checking_df.Balance, '+', label='Balance')
        a.plot(self.checking_df.days, self.checking_df.select_balance, '-', label='Select Balance (no JnJ income or internal tnsf)')
        a.plot(self.spend_X, self.spend_Y, 'o', label=f'fit region ({self.spend_is_clean_after_this} on)')
        a.plot(self.spend_X, self.spend_fit(self.spend_X), '--', label='fit')
        a.plot(self.checking_df.days, self.checking_df.test_balance, '*', label='Test Balance')
        a.legend()
    
    def general_analysis(self):
        
        crit = (self.all_chase_df['no_num_description'].str.lower().str.contains('itunes') &\
        self.all_chase_df['no_num_description'].str.lower().str.contains('bill'))
        self.itunes_spend = self.all_chase_df.loc[crit].Amount.sum()

        crit = (self.all_chase_df['no_num_description'].str.lower().str.contains('j&j'))
        self.mark_income_df = self.all_chase_df.loc[crit]
        
    
    def print_summary(self):
        self.general_analysis()
        
        print((f"Based on cleaned checking, the spend rate is "
               f"${round(-self.spend_dollars_per_day, 2)}/day"))
        
        print((f"You are assuming that spend data is clean after "
               f"{self.spend_is_clean_after_this}"))
        
        print(f"Itunes spend is ${abs(round(self.itunes_spend,2))} total")
        
        
if __name__ == '__main__':
    sa = SpendAnalysis()
    sa.print_summary()
    
    sa.raw_chase_plot()
    sa.fit_spend_plot()
    
    bc = BudgetConstants()
    bc.print_vars()