from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_spend import SpendAnalysis
from secret_constants import Constants

pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)

class Retirement():
    """"""

    def __init__(self, SpendAnalysis, Constants, previous_df, monte_carlo=0):
        self.c = Constants
        self.c.generate_constants(monte_carlo)
        self.sa = SpendAnalysis

        self.previous_df = previous_df

        # Create DataFrame to hold all phase 2 period projections
        self.retirement_start = self.previous_df.Payment_Date.values[-1] # TODO: assert that the last df ends near retirement date
        self.retirement_end = self.c.death_date
        self.main_df = self.make_empty_timeseries_df(self.retirement_start,
                                                     self.retirement_end)

        self.add_future_acount_values_to_main_df()
        #self.add_empirical_chase_projections_to_main_df()
        #self.add_theoretical_chase_projections_to_main_df()

        # Combine previous df with main df
        self.combo_df = pd.concat([self.previous_df, self.main_df],
                                  ignore_index=True, verify_integrity=True, sort=True)

    def plot(self):
        f, a = plt.subplots(nrows=3, ncols=1)
        e_chase = a[0]
        t_chase = a[1]
        wealth = a[2]

        wealth.plot(self.combo_df.Payment_Date, self.combo_df.Wealthfront)
        wealth.set_ylabel('Wealthfront Balance')
        t_chase.plot(self.combo_df.Payment_Date, self.combo_df['Theoretical_Chase'])
        t_chase.set_ylabel('Theoretical Chase Balance')
        e_chase.plot(self.combo_df.Payment_Date, self.combo_df['Empirical_Chase'])
        e_chase.set_ylabel('Empirical Chase Balance')

        f, a = plt.subplots(ncols=1, nrows=2)
        a[0].plot(self.combo_df.Payment_Date, self.combo_df.roth_principal)
        a[0].set_ylabel('Roth Principal')
        a[1].plot(self.combo_df.Payment_Date, self.combo_df.IRA_principal)
        a[1].set_ylabel('IRA Principal')
        plt.show()

    def summarize(self):

        print(f"Castle Downpayment is {self.c.castle_downpayment} (assuming {self.c.castle_downpayment_percent}%)")
        print(f"Your equity in OLeary = {self.previous_df.oleary_cumulative_principal.values[-1]}")

    def add_castle_amortization_info(self):
        """Calculate monthly principal and interest payment for the new 'Castle' we are buying.
        Use those to calculate the accumulated principle at a given time"""

        self.main_df['castle_principal_payment'] = np.ppmt(self.c.castle_rate / 12,
                                                   self.main_df.index,
                                                   self.c.castle_payment_years * 12,
                                                   self.c.castle_principal)
        self.main_df['castle_interest_payment'] = np.ipmt(self.c.castle_rate / 12,
                                                  self.main_df.index,
                                                  self.c.castle_payment_years * 12,
                                                  self.c.castle_principal)

        self.main_df['castle_cumulative_principal'] = self.main_df['castle_principal_payment'].abs().cumsum()

    def make_empty_timeseries_df(self, start_date, end_date, cols=[]):
        """Helper function to create a DataFrame with date time format"""
        rng = pd.date_range(start_date, end_date, freq='MS')
        rng.name = "Payment_Date"

        df = pd.DataFrame(index=rng, columns=cols, dtype='float')
        df.reset_index(inplace=True)
        df.index += 1
        df.index.name = "Period"

        return df

    def add_future_acount_values_to_main_df(self):
        """Calculate future value of investments starting with previous"""

        compounds_per_year = 12
        self.main_df['Wealthfront'] = np.fv(self.c.wealthfront_rate / compounds_per_year,
                                            self.main_df.index,
                                            -0,
                                            -self.previous_df.Wealthfront.values[-1])

        self.main_df['IRA_principal'] = np.fv(self.c.IRA_rate / compounds_per_year,
                                              self.main_df.index,
                                              self.c.monthly_IRA_withdrawal,
                                              -self.previous_df.IRA_principal.values[-1]) # TODO: account for taxes

        self.main_df['roth_principal'] = np.fv(self.c.roth_rate / compounds_per_year,
                                               self.main_df.index,
                                               self.c.monthly_roth_withdrawal,
                                               -self.previous_df.roth_principal.values[-1]) # TODO: account for taxes

        self.main_df['hsa_principal'] = np.fv(self.c.HSA_rate / compounds_per_year,
                                              self.main_df.index,
                                              0,
                                              -self.previous_df.hsa_principal.values[-1])

    def add_empirical_chase_projections_to_main_df(self):
        """Use historic empirical SpendAnalysis projections to predict Chase balance """

        house_sale_balance = self.previous_df.oleary_cumulative_principal.values[-1] - self.c.castle_downpayment

        oleary_payment = np.pmt(self.c.oleary_rate / 12,
                                self.c.oleary_payment_years * 12,
                                self.c.oleary_principal)

        castle_payment = np.pmt(self.c.castle_rate / 12,
                                self.c.castle_payment_years * 12,
                                self.c.castle_principal)

        additional_monthly_expenses = (abs(castle_payment) - abs(oleary_payment)) + \
                                      (abs(self.c.castle_monthly_insurance) - abs(self.c.oleary_monthly_insurance)) + \
                                      (abs(self.c.castle_monthly_taxes) - abs(self.c.oleary_monthly_taxes))

        # TODO: estimate increase in montly home related costs (insurance, energy, cleaning, etc)
        self.main_df['Empirical_Chase'] = (self.sa.save_dollars_per_day * 30 - additional_monthly_expenses) * self.main_df.index + \
                                          (self.previous_df.Empirical_Chase.values[-1] + house_sale_balance)
        pass
    def add_theoretical_chase_projections_to_main_df(self):
        """Calculate savings based on Spend Analysis flow and Secret Constants projections.
         Add as column to main_df"""

        pre_tax_deductions = (self.c.bi_weekly_IRA_contribution +
                              self.c.bi_weekly_hsa_contribution +
                              self.c.bi_weekly_medical) * 2

        marks_adjusted_wages = -np.fv(self.c.marks_wages_growth,
                                     np.floor(self.main_df.index / 12),
                                     0,
                                     self.c.daily_pre_tax_mark)

        monthly_pre_tax_income = (marks_adjusted_wages * 30 - pre_tax_deductions)

        self.oleary_payment = np.pmt(self.c.oleary_rate / 12,
                                     self.c.oleary_payment_years * 12,
                                     self.c.oleary_principal)

        self.castle_payment = np.pmt(self.c.castle_rate / 12,
                                     self.c.castle_payment_years * 12,
                                     self.c.castle_principal)

        mortgage_payment_diff = abs(self.castle_payment) - abs(self.oleary_payment)
        assert mortgage_payment_diff > 0

        post_tax_deductions = ((self.c.bi_weekly_roth_contribution +
                                self.c.bi_weekly_life_dissability) * 2 +
                                mortgage_payment_diff)

        monthly_post_tax_income = monthly_pre_tax_income * (1 - self.c.tax_rate) - post_tax_deductions

        house_sale_balance = self.previous_df.oleary_cumulative_principal.values[-1] - self.c.castle_downpayment
        self.main_df['Theoretical_Chase'] = (monthly_post_tax_income + self.sa.spend_dollars_per_day * 30) * self.main_df.index + \
                                (self.previous_df.Theoretical_Chase.values[-1] + house_sale_balance)




if __name__ == '__main__':
    exit()