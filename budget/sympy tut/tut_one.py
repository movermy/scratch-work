# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 22:17:33 2019

@author: movermye
"""

from sympy import symbols
from sympy import expand, factor
from sympy.plotting import plot
from sympy.functions.special.delta_functions import Heaviside
from mpmath import e
import matplotlib.pyplot as plt

plt.close('all')



x, y, t = symbols('x y t')
P = 409
r = .07
marks_earnings = P * e ** (r * (t-0)) * Heaviside(t-0)
P = 100
r = .03
karens_earnings = P * e ** (r * (t-3)) * Heaviside(t-3)
total_earnings = marks_earnings + karens_earnings

offset = x - 5
my_line = 1 * (offset) * Heaviside(offset)




plot(total_earnings)
plot(my_line)