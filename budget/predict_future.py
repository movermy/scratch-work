# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date

from analyze_spend import SpendAnalysis
from secret_constants import Constants
import predict_future_tools as tools

# configure globals
pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)

sa = SpendAnalysis()
c = Constants()

''' Just extrapolate the present conditions '''

df = tools.make_empty_timeseries_df((date(2019, 5, 3)), (date(2020, 5, 3)))

tools.add_future_acount_values(df, c)


# build chase cash flow
pre_tax_deductions = (c.bi_weekly_IRA_contribution +
                      c.bi_weekly_hsa_contribution +
                      c.bi_weekly_medical) * 2

monthly_pre_tax_income = (c.daily_pre_tax_mark * 30 - pre_tax_deductions)

post_tax_deductions = ((c.bi_weekly_roth_contribution +
                        c.bi_weekly_life_dissability) * 2)

monthly_post_tax_income = monthly_pre_tax_income * (1 - c.tax_rate) - post_tax_deductions

df['Chase'] = (monthly_post_tax_income + sa.spend_dollars_per_day * 30) * df.index + c.chase_start_amount

# OLeary mortgage
oldf = tools.make_empty_timeseries_df((date(2010, 4, 3)), (date(2020, 5, 3)))

oleary_payment = np.pmt(c.oleary_rate/12,
                        c.oleary_payment_years*12,
                        c.oleary_principal)

print(f"Calculated ${oleary_payment}/month on oleary") #TODO: check olear amortization agains actual

oldf['oleary_principal_payment'] = np.ppmt(c.oleary_rate/12,
                                         oldf.index,
                                         c.oleary_payment_years*12,
                                         c.oleary_principal)
oldf['oleary_interest_payment'] = np.ipmt(c.oleary_rate/12,
                                         oldf.index,
                                         c.oleary_payment_years*12,
                                         c.oleary_principal)

oldf['oleary_cumulative_principal'] = oldf['oleary_principal_payment'].abs().cumsum()

#tools.plot_oleary_data(oldf)


# combine mortgage df with main df
df = pd.merge(df, oldf, on=['Payment_Date']) #TODO there is probably a more efficient way to do this
print(df.round(2).head())

tools.plot_overall_summary(df)
#chase.xlabel('Chase Bank total balance')











plt.show()

