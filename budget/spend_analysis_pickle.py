import pickle
import os
import matplotlib.pyplot as plt
from analyze_spend import SpendAnalysis #gotta do this so pickles made externally work. See link below
# https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html


start_dir = os.getcwd()
os.chdir(r"spend analysis pickles")
before = pickle.load( open( "erase-this.p", "rb" ) )
after = pickle.load( open( r"with_march.p", "rb" ) )
os.chdir(start_dir)


b = before.fit_plot()
print(b.set_title('Before'))

a = after.fit_plot()
print(a.set_title('after'))

plt.show()