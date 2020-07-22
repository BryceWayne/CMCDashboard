# dataframe.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle, os

cwd = os.getcwd()
with open(f'{cwd}/data/test.pkl', 'rb') as f:
	data = pickle.load(f)

history = data['History']

df = pd.DataFrame(history)

df.plot()
plt.show()
