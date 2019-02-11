# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 18:10:27 2019

@author: MOvermye
"""

import datetime
import matplotlib.pyplot as plt
import math
plt.close('all')

karen_birthday = datetime.date(year=1985, month=7, day=30)
mark_birthday = datetime.date(year=1986, month=1, day=20)
bruce_birthday = datetime.date(year=2018, month=2, day=6)
glen_birthday = datetime.date(year=2015, month=6, day=2)

print(f"There are {bruce_birthday-mark_birthday} between mark and bruce's birthday")

# this is a technique for making a range of date, which can be used in a plot
time = [datetime.date.today() + datetime.timedelta(days=i) for i in range(365 * 3)]


f, a = plt.subplots(1,1)
a.plot([karen_birthday, mark_birthday, glen_birthday, bruce_birthday],
       ['karen', 'mark', 'glen', 'bruce'], '*')

plt.show()

class Cash_Flow:
    def __init__(self, value, 
                 start=datetime.date.today(), 
                 finish=datetime.date.today() + datetime.timedelta(days=365*100), 
                 interval_days=1, 
                 yearly_interest_percent=0):
        self.value = value #amount of money flow. Positive is incomming
        
        self.start = start #datetime date of start
        self.finish = finish #datetime date of finish, if needed
        self.interval_days = interval_days #recurrence of event, in days
        self.yearly_interest_percent = yearly_interest_percent 
        
    def get_flow(self, now):
        
        period = now - self.start
        self.interest_multi = ((1 + self.yearly_interest_percent/100) ** math.ceil(period.days/365))
        if (period.days % self.interval_days == 0):
            return (self.value * self.interest_multi)
        else:
            return 0
  
starting_savings = 10000


marks_take_home = Cash_Flow(2000, interval_days=14,
                            yearly_interest_percent=5)

groceries = Cash_Flow(-125, interval_days=7,
                      yearly_interest_percent=4)

flows = [marks_take_home, groceries]


savings = []
for idx, day in enumerate(time):
    
    if idx == 0:
        savings += [starting_savings]
    else:
        savings += [savings[-1] + marks_take_home.get_flow(day) + groceries.get_flow(day)]
    
f, a = plt.subplots(1,1)
a.plot(time, savings)
    
    