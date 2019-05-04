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

# configure globals
pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)
plt.close('all')
#plt.ion()


sa = SpendAnalysis()
c = Constants()
days = symbols('days')



''' Just extrapolate the present conditions '''
# create a nice dataframe

start_date = (date(2019,5,3))
end_date = (date(2020,5,3))
rng = pd.date_range(start_date, end_date, freq='MS')
rng.name = "Payment_Date"

cols = ['Wealthfront', 'Chase', 'IRA_principal', 'roth_principal', 'hsa_principal']
df = pd.DataFrame(index=rng, columns=cols, dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "Period"

compounds_per_year = 12
df.Wealthfront = np.fv(c.wealthfront_rate/compounds_per_year,
                       df.index,
                       -0,
                       -c.wealthfront_principal)

df.IRA_principal = np.fv(c.IRA_rate/compounds_per_year,
                         df.index,
                         -c.bi_weekly_IRA_contribution * 2,
                         -c.IRA_principal)

df.roth_principal = np.fv(c.roth_rate/compounds_per_year,
                          df.index,
                          -c.bi_weekly_roth_contribution * 2,
                          -c.roth_principal)

df.hsa_principal = np.fv(c.HSA_rate/compounds_per_year,
                         df.index,
                         -c.bi_weekly_hsa_contribution * 2,
                         -c.HSA_principal)


# build chase cash flow
pre_tax_deductions = (c.bi_weekly_IRA_contribution +
                      c.bi_weekly_hsa_contribution +
                      c.bi_weekly_medical) * 2

monthly_pre_tax_income = (c.daily_pre_tax_mark * 30 - pre_tax_deductions)

post_tax_deductions = ((c.bi_weekly_roth_contribution +
                        c.bi_weekly_life_dissability) * 2)

monthly_post_tax_income = monthly_pre_tax_income * (1 - c.tax_rate) - post_tax_deductions

df.Chase = (monthly_post_tax_income + sa.spend_dollars_per_day * 30) * df.index + c.chase_start_amount

#OLeary mortgage
start_date = (date(2010, 4, 3))
end_date = (date(2020, 5, 3))
rng = pd.date_range(start_date, end_date, freq='MS')
rng.name = "Payment_Date"

oldf = pd.DataFrame(index=rng, columns=['oleary_principal_payment'], dtype='float')
oldf.reset_index(inplace=True)
oldf.index += 1
oldf.index.name = "Period"

oleary_payment = np.pmt(c.oleary_rate/12,
             c.oleary_payment_years*12,
             c.oleary_principal)
print(f"Calculated ${oleary_payment}/month on oleary")
oldf['oleary_principal_payment'] = np.ppmt(c.oleary_rate/12,
                                         oldf.index,
                                         c.oleary_payment_years*12,
                                         c.oleary_principal)
oldf['oleary_interest_payment'] = np.ipmt(c.oleary_rate/12,
                                         oldf.index,
                                         c.oleary_payment_years*12,
                                         c.oleary_principal)

oldf['oleary_cumulative_principal'] = oldf['oleary_principal_payment'].abs().cumsum()

fig, ax = plt.subplots(figsize=(20, 10))
fig.suptitle('OLeary Mortgage')
ln1 = ax.plot(oldf.Payment_Date, oldf.oleary_cumulative_principal, label='cumu principle', color='k')
ax2 = ax.twinx()
ln2 = ax2.plot(oldf.Payment_Date, -oldf.oleary_principal_payment, label='principle payment', color = 'g')
ln3 = ax2.plot(oldf.Payment_Date, -oldf.oleary_interest_payment, label='interest payment', color = 'r')
lns = ln1+ln2+ln3
labs = [l.get_label() for l in lns]
ax2.legend(lns, labs, loc=0)
print(oldf.head())


# combine mortgage df with main df
df = pd.merge(df, oldf, on=['Payment_Date']) #TODO there is probably a more efficient way to do this
print(df.round(2).head())
plt.show()

