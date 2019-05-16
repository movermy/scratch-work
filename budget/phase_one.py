from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_spend import SpendAnalysis
from secret_constants import Constants

pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)

class PhaseOne():
    """This class handles the financial info for the current state. Current state being early 2019. It uses the spend
    analysis from the past few years, as well as estimated parameters about things like growth rate to create near-
    term projects. The ultimate result is a time series DataFrame with financial projections"""

    def __init__(self, SpendAnalysis, Constants, monte_carlo=0):
        self.c = Constants
        self.c.generate_constants(monte_carlo)
        self.sa = SpendAnalysis

        # Create DataFrame to hold all phase 1 period projections
        self.phase_one_start = (date(2019, 5, 1))
        self.phase_one_end = (date(2020, 5, 1))
        self.main_df = self.make_empty_timeseries_df(self.phase_one_start,
                                                     self.phase_one_end)
        self.add_future_acount_values_to_main_df()
        self.add_chase_projections_to_main_df()

        # Create DataFrame for OLeary mortgage
        self.oleary_start = (date(2010, 4, 1))
        self.oleary_end = self.oleary_start + timedelta(days=15*365)
        self.oleary_df = self.make_empty_timeseries_df(self.oleary_start,
                                                       self.oleary_end)
        self.add_oleary_amortization_info()

        # Merge OLeary DataFrame in to main, but just the phase 1 region
        self.main_df = pd.merge(self.main_df,
                                self.oleary_df,
                                on=['Payment_Date']) #TODO there is probably a more efficient way to do this


    def summarize_oleary(self):
        """Print and plot descriptive info of the OLeary mortgage"""

        self.plot_oleary_data()

        oleary_payment = np.pmt(self.c.oleary_rate / 12,
                                self.c.oleary_payment_years * 12,
                                self.c.oleary_principal)

        print_header = f"### Pooping out Oleary Mortgage summary ###"
        print_body = f"Calculated ${round(oleary_payment, 2)}/month on oleary"  # TODO: check oleary amortization against actual
        print_footer = f"### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###"

        print("\n" + print_header + "\n" + print_body + "\n" + print_footer + "\n")

    def add_oleary_amortization_info(self):
        """Calculate monthly principal and interest payment.
        Use those to calculate the accumulated principle at a given time"""

        self.oleary_df['oleary_principal_payment'] = np.ppmt(self.c.oleary_rate / 12,
                                                   self.oleary_df.index,
                                                   self.c.oleary_payment_years * 12,
                                                   self.c.oleary_principal)
        self.oleary_df['oleary_interest_payment'] = np.ipmt(self.c.oleary_rate / 12,
                                                  self.oleary_df.index,
                                                  self.c.oleary_payment_years * 12,
                                                  self.c.oleary_principal)

        self.oleary_df['oleary_cumulative_principal'] = self.oleary_df['oleary_principal_payment'].abs().cumsum()

    def make_empty_timeseries_df(self, start_date, end_date, cols=[]):
        """Helper function to create a DataFrame with date time format"""
        rng = pd.date_range(start_date, end_date, freq='MS')
        rng.name = "Payment_Date"

        df = pd.DataFrame(index=rng, columns=cols, dtype='float')
        df.reset_index(inplace=True)
        df.index += 1
        df.index.name = "Period"

        return df

    def add_chase_projections_to_main_df(self, verbose=False):
        """Calculate savings based on Spend Analysis flow and Secret Constants projections.
         Add as column to main_df"""

        pre_tax_deductions = (self.c.bi_weekly_IRA_contribution +
                              self.c.bi_weekly_hsa_contribution +
                              self.c.bi_weekly_medical) * 2

        if verbose: print(f"total pre-tax deductions: {pre_tax_deductions}/month")

        marks_adjusted_wages = -np.fv(self.c.marks_wages_growth,
                                     np.floor(self.main_df.index / 12),
                                     0,
                                     self.c.daily_pre_tax_mark)

        if verbose: print(f"Marks earns &{marks_adjusted_wages.min()}/day (min), ${marks_adjusted_wages.mean()}/day (average), for this phase")
        if verbose: print(f"That's ${marks_adjusted_wages.mean() * 365} per year")

        monthly_pre_tax_income = (marks_adjusted_wages * 30 - pre_tax_deductions)

        if verbose: print(f"Pre-tax, after deductions, mark gets ${monthly_pre_tax_income.mean()}/month")
        if verbose: print(f"Pre-tax, after deductions, mark gets ${monthly_pre_tax_income.mean()/30}/day")
        if verbose: print(f"That's ${monthly_pre_tax_income.mean() * 12} per year remaining")

        post_tax_deductions = ((self.c.bi_weekly_roth_contribution +
                                self.c.bi_weekly_life_dissability) * 2)

        if verbose: print(f"Post tax deductions are {post_tax_deductions}/month")

        monthly_post_tax_income = monthly_pre_tax_income * (1 - self.c.tax_rate) - post_tax_deductions

        if verbose: print(f"Average post tax income is ${monthly_post_tax_income.mean()}/month")
        if verbose: print(f"Average post tax income is ${monthly_post_tax_income.mean() / 30}/day")
        if verbose: print(f"Average post tax income is ${monthly_post_tax_income.mean() * 12}/year")

        if verbose: print(f"You spend {self.sa.spend_dollars_per_day * 30}/month")
        self.main_df['Chase'] = (monthly_post_tax_income + self.sa.spend_dollars_per_day * 30) * self.main_df.index + \
                                self.c.chase_start_amount

    def add_future_acount_values_to_main_df(self):
        """Calculate future value of investments and adds them as columns to the main_df"""

        compounds_per_year = 12
        self.main_df['Wealthfront'] = np.fv(self.c.wealthfront_rate / compounds_per_year,
                                            self.main_df.index,
                                            -0,
                                            -self.c.wealthfront_principal)

        self.main_df['IRA_principal'] = np.fv(self.c.IRA_rate / compounds_per_year,
                                              self.main_df.index,
                                              -self.c.bi_weekly_IRA_contribution * 2,
                                              -self.c.IRA_principal)

        self.main_df['roth_principal'] = np.fv(self.c.roth_rate / compounds_per_year,
                                               self.main_df.index,
                                               -self.c.bi_weekly_roth_contribution * 2,
                                               -self.c.roth_principal)

        self.main_df['hsa_principal'] = np.fv(self.c.HSA_rate / compounds_per_year,
                                              self.main_df.index,
                                              -self.c.bi_weekly_hsa_contribution * 2,
                                              -self.c.HSA_principal)

    def plot_oleary_data(self):
        fig, ax = plt.subplots(figsize=(20, 10))
        fig.suptitle('OLeary Mortgage')
        ln1a = ax.plot(self.oleary_df.Payment_Date, self.oleary_df.oleary_cumulative_principal, label='cumu principle', color='k')
        ln1b = ax.plot([self.phase_one_end, self.phase_one_end],
                       [self.oleary_df.oleary_cumulative_principal.min(), self.oleary_df.oleary_cumulative_principal.max()],
                       color='y',
                       label='End of Phase 1')
        ln1c = ax.plot([self.phase_one_start, self.phase_one_start],
                       [self.oleary_df.oleary_cumulative_principal.min(), self.oleary_df.oleary_cumulative_principal.max()],
                       color='b',
                       label='Beginning of Phase 1')
        ax2 = ax.twinx()
        ln2 = ax2.plot(self.oleary_df.Payment_Date, -self.oleary_df.oleary_principal_payment, label='principle payment', color='g')
        ln3 = ax2.plot(self.oleary_df.Payment_Date, -self.oleary_df.oleary_interest_payment, label='interest payment', color='r')
        lns = ln1a+ln1c+ln1b+ln2+ln3
        labs = [l.get_label() for l in lns]
        ax2.legend(lns, labs, loc=0)


    def plot_overall_summary(self):
        fig, ax = plt.subplots(ncols=1, nrows=3, figsize=(40, 20))
        fig.suptitle('Summary of Early 2019 finances')

        oleary = ax[0]  # type:axes.Axes
        ln1 = oleary.plot(self.main_df.Payment_Date, self.main_df.oleary_cumulative_principal, label='cumu principle', color='k')
        oleary2 = oleary.twinx()
        ln2 = oleary2.plot(self.main_df.Payment_Date, -self.main_df.oleary_principal_payment, label='principle payment', color='g')
        ln3 = oleary2.plot(self.main_df.Payment_Date, -self.main_df.oleary_interest_payment, label='interest payment', color='r')
        lns = ln1 + ln2 + ln3
        labs = [l.get_label() for l in lns]
        oleary2.legend(lns, labs, loc=0)
        oleary.set_title('Oleary Mortgage')

        retirement = ax[1]  # type:axes.Axes
        retirement.plot(self.main_df.Payment_Date, self.main_df.Wealthfront, label='Projected Wealthfront')
        retirement.plot(self.main_df.Payment_Date, self.main_df.roth_principal, label='Projected roth')
        retirement.plot(self.main_df.Payment_Date, self.main_df.hsa_principal, label='Projected HSA')
        retirement.plot(self.main_df.Payment_Date, self.main_df.IRA_principal, label='Projected IRA')
        retirement.legend()
        retirement.set_title('Investment Projections')

        chase = ax[2]  # type:axes.Axes
        chase.plot(self.main_df.Payment_Date, self.main_df.Chase)
        chase.set_title("Chase bank ballance, all accounts")

if __name__ == '__main__':
    p1 = PhaseOne(SpendAnalysis(), Constants())

    p1.summarize_oleary()

    p1.plot_overall_summary()

    p1.add_chase_projections_to_main_df(verbose=True)

    plt.show()