# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:21:03 2019

@author: movermye
"""

import pandas as pd
import os

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
        
        return combo_df
 
card_df = chase_csv_import("card-data")
card_df['source'] = 'card'
checking_df = chase_csv_import("checking-data")
checking_df['source'] = 'checking'
savings_df = chase_csv_import("savings-data")
savings_df['source'] = 'savings'

df = pd.concat([card_df, checking_df, savings_df], 
               ignore_index=True, sort=True)

