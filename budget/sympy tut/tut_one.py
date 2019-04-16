# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 22:17:33 2019

@author: movermye
"""

from sympy import symbols
from sympy import expand, factor
from sympy.plotting import plot
from sympy.functions.special.delta_functions import Heaviside

x, y = symbols('x y')

expr = x + 2*y

my_line = 1 * (x - 5) * Heaviside(x - 5)

p1 = plot(my_line)