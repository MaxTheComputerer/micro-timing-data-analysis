import pandas as pd
from tabulate import tabulate
from pathlib import Path
import matplotlib.pyplot as plt

files = Path().glob(f'data/*Jembe-2.csv')
#11
dfs = []
for file in files:
    df = pd.read_csv(file)
    df = df[df['Is_included_in_grid'] == 1]
    df = df[df['Metric_location'].isin([0,1,2,3])]
    df['Tempo'] = 60 / (df.Onset_time - df.Onset_time.shift(1))
    df['First_onset'] = df['Onset_time'].iloc[0]
    df['Relative_onset'] = df['Onset_time'] - df['First_onset']
    plt.plot(df['Relative_onset'], df['Tempo'], linewidth=0.5, alpha=0.5, color='gray')
    dfs.append(df)

df = pd.concat(dfs)

m = df.groupby(['Cycle_number', 'Metric_location']).mean()
plt.plot(m['Relative_onset'], m['Tempo'])
#print(tabulate(m,headers="keys"))
plt.show()
