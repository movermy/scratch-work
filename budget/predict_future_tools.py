from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)




def make_empty_timeseries_df(start_date, end_date, cols=[]):
    rng = pd.date_range(start_date, end_date, freq='MS')
    rng.name = "Payment_Date"

    df = pd.DataFrame(index=rng, columns=cols, dtype='float')
    df.reset_index(inplace=True)
    df.index += 1
    df.index.name = "Period"

    return df

def plot_oleary_data(oldf):
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.suptitle('OLeary Mortgage')
    ln1 = ax.plot(oldf.Payment_Date, oldf.oleary_cumulative_principal, label='cumu principle', color='k')
    ax2 = ax.twinx()
    ln2 = ax2.plot(oldf.Payment_Date, -oldf.oleary_principal_payment, label='principle payment', color='g')
    ln3 = ax2.plot(oldf.Payment_Date, -oldf.oleary_interest_payment, label='interest payment', color='r')
    lns = ln1+ln2+ln3
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=0)

def add_future_acount_values(df, c):

    compounds_per_year = 12
    df['Wealthfront'] = np.fv(c.wealthfront_rate/compounds_per_year,
                           df.index,
                           -0,
                           -c.wealthfront_principal)

    df['IRA_principal'] = np.fv(c.IRA_rate/compounds_per_year,
                             df.index,
                             -c.bi_weekly_IRA_contribution * 2,
                             -c.IRA_principal)

    df['roth_principal'] = np.fv(c.roth_rate/compounds_per_year,
                              df.index,
                              -c.bi_weekly_roth_contribution * 2,
                              -c.roth_principal)

    df['hsa_principal'] = np.fv(c.HSA_rate/compounds_per_year,
                             df.index,
                             -c.bi_weekly_hsa_contribution * 2,
                             -c.HSA_principal)
    return df

def plot_overall_summary(df):
    fig, ax = plt.subplots(ncols=1, nrows=3, figsize=(40, 20))
    fig.suptitle('Summary of Early 2019 finances')

    oleary = ax[0]  # type:axes.Axes
    ln1 = oleary.plot(df.Payment_Date, df.oleary_cumulative_principal, label='cumu principle', color='k')
    oleary2 = oleary.twinx()
    ln2 = oleary2.plot(df.Payment_Date, -df.oleary_principal_payment, label='principle payment', color='g')
    ln3 = oleary2.plot(df.Payment_Date, -df.oleary_interest_payment, label='interest payment', color='r')
    lns = ln1 + ln2 + ln3
    labs = [l.get_label() for l in lns]
    oleary2.legend(lns, labs, loc=0)
    oleary.set_title('Oleary Mortgage')

    retirement = ax[1]  # type:axes.Axes
    retirement.plot(df.Payment_Date, df.Wealthfront, label='Projected Wealthfront')
    retirement.plot(df.Payment_Date, df.roth_principal, label='Projected roth')
    retirement.plot(df.Payment_Date, df.hsa_principal, label='Projected HSA')
    retirement.plot(df.Payment_Date, df.IRA_principal, label='Projected IRA')
    retirement.legend()
    retirement.set_title('Investment Projections')

    chase = ax[2]  # type:axes.Axes
    chase.plot(df.Payment_Date, df.Chase)
    chase.set_title("Chase bank ballance, all accounts")

if __name__ == '__main__':
    start_date = (date(2019, 5, 3))
    end_date = (date(2020, 5, 3))
    cols = []

    df = make_empty_timeseries_df(start_date, end_date, cols)

    print(df.head())