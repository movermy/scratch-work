from datetime import date
import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('expand_frame_rep', False)



def make_empty_timeseries_df(start_date, end_date, cols):
    rng = pd.date_range(start_date, end_date, freq='MS')
    rng.name = "Payment_Date"

    df = pd.DataFrame(index=rng, columns=cols, dtype='float')
    df.reset_index(inplace=True)
    df.index += 1
    df.index.name = "Period"

    return df

if __name__ == '__main__':
    start_date = (date(2019, 5, 3))
    end_date = (date(2020, 5, 3))
    cols = []

    df = make_empty_timeseries_df(start_date, end_date, cols)

    print(df.head())