import pickle
import os
import matplotlib.pyplot as plt
from analyze_spend import SpendAnalysis #gotta do this so pickles made externally work. See link below
# https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html


start_dir = os.getcwd()
os.chdir(r"spend analysis pickles")
sa = pickle.load( open( "erase-this.p", "rb" ) )
sa2 = pickle.load( open( r"erase-this.p", "rb" ) )
os.chdir(start_dir)


a1 = sa.fit_plot()
print(a1.set_title('a1'))

a2 = sa2.fit_plot()
print(a2.set_title('a2'))


plt.show()