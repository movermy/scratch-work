from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_spend import SpendAnalysis
from secret_constants import Constants

pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)

class PhaseTwo():
    """"""

    def __init__(self, SpendAnalysis, Constants, previous_df, monte_carlo=0):
        self.c = Constants
        self.c.generate_constants(monte_carlo)
        self.sa = SpendAnalysis

        self.previous_df = previous_df

        # Create DataFrame to hold all phase 2 period projections
        self.phase_two_start = self.previous_df.Payment_Date.values[-1] #TODO: add one month to this
        self.phase_two_end = self.c.retirement_date
        self.main_df = self.make_empty_timeseries_df(self.phase_two_start,
                                                     self.phase_two_end)

        self.add_future_acount_values_to_main_df()
        self.add_empirical_chase_projections_to_main_df()
        self.add_theoretical_chase_projections_to_main_df()

        # Combine previous df with main df
        self.combo_df = pd.concat([self.previous_df, self.main_df],
                                  ignore_index=True, verify_integrity=True, sort=True)
        self.summarize()
        self.plot()
    def plot(self):
        f, a = plt.subplots()

        a.plot(self.combo_df.Payment_Date, self.combo_df.Wealthfront)
        a.plot(self.combo_df.Payment_Date, self.combo_df.Chase)
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
                                              -self.c.bi_weekly_IRA_contribution * 2,
                                              -self.previous_df.IRA_principal.values[-1])

        self.main_df['roth_principal'] = np.fv(self.c.roth_rate / compounds_per_year,
                                               self.main_df.index,
                                               -self.c.bi_weekly_roth_contribution * 2,
                                               -self.previous_df.roth_principal.values[-1])

        self.main_df['hsa_principal'] = np.fv(self.c.HSA_rate / compounds_per_year,
                                              self.main_df.index,
                                              -self.c.bi_weekly_hsa_contribution * 2,
                                              -self.previous_df.hsa_principal.values[-1])

    def add_empirical_chase_projections_to_main_df(self):
        """Use historic empirical SpendAnalysis projections to predict Chase balance """

        house_sale_balance = self.previous_df.oleary_cumulative_principal.values[-1] - self.c.castle_downpayment

        # TODO: estimate increase in montly home related costs (insurance, energy, cleaning, etc)
        self.main_df['Empirical_Chase'] = (self.sa.save_dollars_per_day * 30) * self.main_df.index + \
                                            (self.previous_df.Empirical_Chase.values[-1] + house_sale_balance)

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