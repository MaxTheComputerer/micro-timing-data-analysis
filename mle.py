import pandas as pd
import numpy as np
from pathlib import Path

files = Path().glob(f'data/*.csv')
df = pd.concat([pd.read_csv(file) for file in files])
df = df[df['Is_included_in_grid'] == 1]
df = df[df['Phase'].notna()]
df['Offset'] = (df['Phase'] - df['Metric_location']) * 3
metric_locations = df['Metric_location'].unique()
metric_locations.sort()

for location in metric_locations:
    series = df[df['Metric_location'] == location]['Offset']
    mean = series.mean()
    stddev = series.std()
    beat = int(np.floor(location))
    pulse_unit = int(np.rint((10/3) * (location - beat)))
    print(beat,',',pulse_unit,',',mean,',',stddev, sep='')
