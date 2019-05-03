# -*- coding: utf-8 -*-
"""
Created on Thu May  2 22:11:04 2019

@author: movermye
"""

''' following the steps in this tutorial:
    https://pbpython.com/amortization-model.html
    '''
    
import pandas as pd
import numpy as np
from datetime import date

# Define the variables for the mortgage
Interest_Rate = 0.04
Years = 30
Payments_Year = 12
Principal = 200000
Addl_Principal = 50
start_date = (date(2019,6,1))

'''Basic use of numpy financial functions '''

# monthly payment
pmt = np.pmt(Interest_Rate/Payments_Year, Years*Payments_Year, Principal) #https://docs.scipy.org/doc/numpy/reference/generated/numpy.pmt.html

# payment portioning
per = Years * 12
interest_payment = np.ipmt(Interest_Rate/Payments_Year, per, Years*Payments_Year, Principal)
principal_payment = np.ppmt(Interest_Rate/Payments_Year, per, Years*Payments_Year, Principal)
print(f"For payment period {per}, you will pay ${-interest_payment} in interest and ${-principal_payment} in principal")

''' Setting up pandas '''
rng = pd.date_range(start_date, periods=Years * Payments_Year, freq='MS')
rng.name = "Payment_Date"

df = pd.DataFrame(index=rng, columns=['Payment', 'Principal', 'Interest', 'Addl_Principal', 'Balance'], dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"

df["Payment"] = np.pmt(Interest_Rate/Payments_Year, Years*Payments_Year, Principal)
df["Principal"] = np.ppmt(Interest_Rate/Payments_Year, df.index, Years*Payments_Year, Principal)
df["Interest"] = np.ipmt(Interest_Rate/Payments_Year, df.index, Years*Payments_Year, Principal)
df["Addl_Principal"] = -Addl_Principal
df = df.round(2)

