# -*- coding: utf-8 -*-


from sympy import symbols
from sympy import expand, factor
from sympy.plotting import plot
from sympy.functions.special.delta_functions import Heaviside
from mpmath import e
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date

from analyze_spend import SpendAnalysis
from secret_constants import Constants

plt.close('all')
#plt.ion()


sa = SpendAnalysis()
c = Constants()
days = symbols('days')


# build cash flow
pre_tax_deductions = (c.bi_weekly_IRA_contribution + 
                      c.bi_weekly_HSA + 
                      c.bi_weekly_medical) / 14

pre_tax_income = (c.daily_pre_tax_mark - pre_tax_deductions)
                 
post_tax_deductions = ((c.bi_weekly_roth_contribution + 
                       c.bi_weekly_life_dissability) / 14) + c.monthly_529_contributions / 30

post_tax_income = pre_tax_income * (1 - c.tax_rate) - post_tax_deductions

daily_flow = post_tax_income * days + sa.spend_dollars_per_day * days 

#TODO: make it so pycharm does not hang on plot

''' Just extrapolate the present conditions '''
# create a nice dataframe

start_date = (date(2019,5,3))
end_date = (date(2020,5,3))
rng = pd.date_range(start_date, end_date, freq='MS')
rng.name = "Payment_Date"

df = pd.DataFrame(index=rng, columns=['Wealthfront', 'Chase'], dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"

annual_interest_rate = c.wealthfront_rate
compounds_per_year = 12
payment = -0
df.Wealthfront = np.fv(c.wealthfront_rate/compounds_per_year,
                       df.index,
                       payment,
                       -c.wealthfront_principal)

df.plot(x='Payment_Date', y='Wealthfront')
plt.show(block=False)

plt.show()



