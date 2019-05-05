# -*- coding: utf-8 -*-

from phase_one import PhaseOne
from analyze_spend import SpendAnalysis
from secret_constants import Constants


p1 = PhaseOne(SpendAnalysis(), Constants())

print(p1.main_df.head())













