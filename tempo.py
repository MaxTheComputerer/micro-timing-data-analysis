import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from config import *

def logf(x, a, b, c):
    return a * np.log(x + b) + c

def quadf(x, a, b, c):
    return (a * (x**2)) + (b * x) + c

def combf(x, a, b, c, d, e, f):
    return np.where(x < TEMPO_CUTOFF, logf(x,a,b,c), quadf(x,d,e,f))

files = Path().glob(f'data/{NAME}/*{JEMBE2}.csv')

dfs = []
for file in files:
    df = pd.read_csv(file)
    df = df[df[VALID] == 1]
    df = df[df[METRIC_LOC].isin([0,1,2,3])]

    if NAME == 'suku':
        df['Tempo'] = 60 / (df.Onset_time - df.Onset_time.shift(1))
    else:
        df['Tempo'] = 60 / (df.onsets_time - df.onsets_time.shift(1))
    first_onset = df[ONSET].iloc[0]
    last_onset = df[ONSET].iloc[-1]
    df['Duration'] = last_onset - first_onset
    df['Progress_raw'] = ((df[ONSET] - first_onset) / df['Duration']) * 100
    df['Progress'] = df['Progress_raw'].round(1)
    df = df.groupby(['Progress'], as_index=False).mean()
    df['Average Tempo'] = df['Tempo'].rolling(window=10).mean()
    plt.plot(df['Progress'], df['Average Tempo'], linewidth=0.5, alpha=0.5, color='gray')
    dfs.append(df)

df = pd.concat(dfs)

m = df.groupby(['Progress'], as_index=False).mean()
m['Average Tempo'] = m['Tempo'].rolling(window=10).mean()
plt.plot(m['Progress'], m['Average Tempo'])

m = m.dropna()
popt,_ = curve_fit(combf, m['Progress'], m['Average Tempo'])
a,b,c,d,e,f = popt
print("Params:",a,b,c,d,e,f)
plt.plot(m['Progress'], combf(m['Progress'],a,b,c,d,e,f))

dur = df['Duration'].unique()
print("Mean duration:", dur.mean())

plt.show()
