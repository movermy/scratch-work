# -*- coding: utf-8 -*-
"""
Created on Thu May  2 23:05:29 2019

@author: movermye
"""

'''Playing with financial np functions'''

import pandas as pd
import numpy as np
from datetime import date



# future value
annual_interest_rate = 0.05
compounds_per_year = 12
years_in_future = 10
present_value = -100
payment = -100
future_value = np.fv(annual_interest_rate/compounds_per_year,
                     years_in_future*compounds_per_year,
                     payment,
                     present_value)
start_date = (date(2019,6,1))
# A nice dataframe
rng = pd.date_range(start_date, periods=Years * Payments_Year, freq='MS')
rng.name = "Payment_Date"

df = pd.DataFrame(index=rng, columns=['Payment', 'Principal', 'Interest', 'Addl_Principal', 'Balance'], dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"
future_values = np.fv(annual_interest_rate/compounds_per_year,
                     df.index,
                     payment,
                     present_value)