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
import pickle
plt.close('all')
pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)


class SpendAnalysis():

    def __init__(self):
        verbose = False
        ''' Create and format a Dataframe for chase credit card'''
        if verbose: print(f"Gathering credit card info")
        self.card_df = self.chase_csv_import("card-data")
        self.card_df['source'] = 'card'
        self.card_df['Date'] =pd.to_datetime(self.card_df['Post Date'])

        ''' Create and format a Dataframe for chase checking. This Dataframe is used
        to estimate cash flow out, so a balance column is created that has been
        corrected for anomalies'''
        if verbose: print(f"Gathering checking info")
        self.checking_df = self.chase_csv_import("checking-data")
        self.checking_df['source'] = 'checking'
        self.checking_df['Date'] = pd.to_datetime(self.checking_df['Posting Date'])
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
        if verbose: print(f"Gathering savings info")
        self.savings_df = self.chase_csv_import("savings-data")
        self.savings_df['source'] = 'savings'
        self.savings_df['Date'] = pd.to_datetime(self.savings_df['Posting Date'])

        # create and format the main df
        self.all_chase_df = pd.concat([self.card_df, self.checking_df, self.savings_df],
               ignore_index=True, sort=True)

        self.all_chase_df.sort_values(by=['Date'], inplace=True)

        self.fit_spend_rate()
        self.fit_savings_rate()
        self.general_analysis()


    def chase_csv_import(self, path):
        # When pointed to a directory of chase bank csv export, this 
        # function creates a DataFrame with all the content. Because
        # duplicates are droped from combo_df, you should be able to 
        # drop csv exports in th efolder willy nilly, though this is
        # not tested
        # TODO: ensure only csvs make it to list
        # TODO: sometimes, exports have #'s when they are not expanded, and cause errors. Fix this.

        csv_name_list = [item_name for item_name in os.listdir(path) if ((item_name.find('.csv') > -1) or ((item_name.find('.CSV') > -1)))]
        df_list = []

        for csv_name in csv_name_list:
            #print(f"now processing csv: {csv_name}")
            df = pd.read_csv(os.path.join(path, csv_name))
            df_list.append(df)

        combo_df = pd.concat(df_list, ignore_index=True)
        combo_df.drop_duplicates(inplace=True)
        combo_df['no_num_description'] = combo_df.Description.str.replace('\d+', '')

        return combo_df

    def raw_chase_plot(self):
        # plot the raw balances for chase related accounts 

        f,a = plt.subplots(ncols=1,nrows=1,figsize=(12, 6))
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

        a.legend()

    def fit_spend_rate(self):

        self.spend_is_clean_after_this = '2017-05-18' #after this day, data is clean
        no_nan_checking = self.checking_df.dropna(subset=['epoch', 'select_balance'])

        crit = (no_nan_checking.Date > self.spend_is_clean_after_this)
        self.spend_X = no_nan_checking.loc[crit].days
        self.spend_Y = no_nan_checking.loc[crit].select_balance
        self.spend_dates = no_nan_checking.loc[crit].Date

        spend_fit_coefficients = np.polyfit(self.spend_X, self.spend_Y, 1)
        self.spend_fit = np.poly1d(spend_fit_coefficients)
        self.spend_dollars_per_day = self.spend_fit[1]

    def fit_savings_rate(self):
        self.savings_fit_start = '2017-09-15'
        self.savings_fit_end = '2019-01-01'
        no_nan_checking = self.checking_df.dropna(subset=['epoch', 'Balance'])

        crit = ((no_nan_checking.Date > self.savings_fit_start) & (no_nan_checking.Date < self.savings_fit_end))
        self.save_X = no_nan_checking.loc[crit].days
        self.save_Y = no_nan_checking.loc[crit].Balance
        self.save_dates = no_nan_checking.loc[crit].Date

        save_fit_coefficients = np.polyfit(self.save_X, self.save_Y, 1)
        self.save_fit = np.poly1d(save_fit_coefficients)
        self.save_dollars_per_day = self.save_fit[1]

    def fit_plot(self):

        f,a = plt.subplots(ncols=1,nrows=1, figsize=(12, 6))
        f.suptitle(f'Spend rate is ${abs(round(self.spend_dollars_per_day, 2))}/day. \n Save rate is ${abs(round(self.save_dollars_per_day))}/day')
        a.plot(self.checking_df.Date, self.checking_df.Balance, '+', label='Balance')
        a.plot(self.checking_df.Date, self.checking_df.select_balance, '-', label='Select Balance (no JnJ income or internal tnsf)')
        a.plot(self.checking_df.Date, self.checking_df.test_balance, '*', label='Test Balance')

        a.plot(self.spend_dates, self.spend_Y, 'o', label=f'spend fit region ({self.spend_is_clean_after_this} on)')
        a.plot(self.spend_dates, self.spend_fit(self.spend_X), '--', label='spend fit')

        a.plot(self.save_dates, self.save_Y, 'o', label=f'save fit region ({self.spend_is_clean_after_this} on)')
        a.plot(self.save_dates, self.save_fit(self.save_X), '--', label='save fit')

        a.legend()

        return a

    def general_analysis(self):

        crit = (self.all_chase_df['no_num_description'].str.lower().str.contains('itunes') &\
        self.all_chase_df['no_num_description'].str.lower().str.contains('bill'))
        self.itunes_spend = self.all_chase_df.loc[crit].Amount.sum()

        crit = (self.all_chase_df['no_num_description'].str.lower().str.contains('j&j'))
        self.mark_income_df = self.all_chase_df.loc[crit]

        # Energy spend analysis
        crit = (self.all_chase_df['no_num_description'].str.lower().str.contains('duke'))
        self.duke_spend = self.all_chase_df.loc[crit].Amount.mean()
        std = self.all_chase_df.loc[crit].Amount.std()

        self.mark_income_df = self.mark_income_df.set_index('Date')
        f,a = plt.subplots(1,1)

        '''
        a.plot( self.mark_income_df.Amount, '*', label='raw')

        window = '30d'
        a.plot(self.mark_income_df.Amount.rolling(window).sum(), label='rolling: '+window)
        a.legend()
        a.set_title('Marks J&J take-home')
        plt.show()

        print(self.mark_income_df.columns)
        '''


    def print_summary(self):
        self.general_analysis()

        print((f"Based on cleaned checking, the spend rate is "
               f"${round(-self.spend_dollars_per_day, 2)}/day"))

        print((f"You are assuming that spend data is clean after "
               f"{self.spend_is_clean_after_this}"))

        print(f"Itunes spend is ${abs(round(self.itunes_spend,2))} total")

    def save(self, fileName):
        """save class instance to pickle file"""

        f = file(fileName, "w")
        pickle.dump(self, f)
        f.close()

    def load(fileName):
        """return class instance from a file"""

        f = file(fileName, "r")
        obj = pickle.load(f)
        f.close()
        return obj
    # make load a static method
    load = staticmethod(load)



if __name__ == '__main__':
    plt.close('all')
    sa = SpendAnalysis()
    sa.print_summary()

    sa.fit_plot()
    plt.show()

    from secret_constants import Constants
    c = Constants()
    print(vars(c))

    #pickle.dump(sa, open("with_march.p", "wb"))
