# -*- coding: utf-8 -*-


from sympy import symbols
from sympy import expand, factor
from sympy.plotting import plot
from sympy.functions.special.delta_functions import Heaviside
from mpmath import e
import matplotlib.pyplot as plt
import pandas as pd

from analyze_spend import SpendAnalysis
from secret_constants import Constants

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

plot(daily_flow)

# build 529 savings
p = 1 # number of periodic payments in the compounding period
n = 12 # the number of times that interest is compounded per unit t
r = 5/100 # the annual interest rate (decimal)
P = 5000 # principle ammount
A = 0 # value of the accrued investment
PMT = 100 # monthly payment
t = 10 # number of years 

compount_interest_for_principal = P*(1+r/n)**(n*t)
future_value_of_a_series = PMT * p * (((1 + r/n)**(n*t) - 1) / (r/n))
total = compount_interest_for_principal + future_value_of_a_series






