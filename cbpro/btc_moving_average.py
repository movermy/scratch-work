# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 12:22:39 2019

@author: movermye
"""

import cbpro

import datetime
import pytz
import matplotlib.pyplot as plt
import numpy as np





public_client = cbpro.PublicClient()


'''
order_book = public_client.get_product_order_book('BTC-USD')

bid_price = order_book['bids'][0][0]
ask_price = order_book['asks'][0][0]

print(f"You can sell BTC for ${bid_price} and buy bitcoin for ${ask_price}")
'''



d = datetime.datetime.utcnow()
utc = pytz.UTC
pst = pytz.timezone('US/Eastern')
d = utc.localize(d) # UTC timezone aware
d = d.astimezone(pst)
end_date = d.isoformat()
end_date = end_date[:-(end_date[::-1].find('-')+1)]
end_date = end_date + 'Z'

delay = 200
d = d - datetime.timedelta(days=delay)

print(f"{d.isoformat()} was {delay} days ago")

start_date = d.isoformat()
start_date = start_date[:-(start_date[::-1].find('-')+1)]
start_date = start_date + 'Z'
history = public_client.get_product_historic_rates('BTC-USD', granularity=86400, start=start_date, end=end_date)

times = []
close_prices = []
for period_result in history:
    time, low, high, open_price, close_price, volume = zip(period_result)
    times.append(time)
    close_prices.append(close_price)

close_prices = np.asarray(close_prices)

plt.close('all')
f,a =plt.subplots()   
a.plot(times, close_prices)
a.title.set_text(f'Closing price from {start_date[0:10]} to {end_date[0:10]}. {delay} day average is ${round(close_prices.mean(),0)}')

plt.show()

    
