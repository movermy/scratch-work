# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

from phase_one import PhaseOne
from phase_two import PhaseTwo
from analyze_spend import SpendAnalysis
from secret_constants import Constants


c = Constants()  #TODO: figure out a way to pass this in to the phase classes
p1 = PhaseOne(SpendAnalysis(), Constants(), monte_carlo=0)
print(p1.main_df.head())

p2 = PhaseTwo(SpendAnalysis(), Constants(), p1.main_df, monte_carlo=0)

p2.plot()
















