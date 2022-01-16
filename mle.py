import pandas as pd
import numpy as np
from pathlib import Path

from config import *

files = Path().glob(f'data/{NAME}/*.csv')
df = pd.concat([pd.read_csv(file) for file in files])
df = df[df[VALID] == 1]
df = df[df[PHASE].notna()]
df['Offset'] = (df[PHASE] - df[METRIC_LOC]) * 3
metric_locations = df[METRIC_LOC].unique()
metric_locations.sort()

for location in metric_locations:
    series = df[df[METRIC_LOC] == location]['Offset']
    mean = series.mean()
    stddev = series.std()
    beat = int(np.floor(location))
    pulse_unit = int(np.rint((10/3) * (location - beat)))
    print(beat,',',pulse_unit,',',mean,',',stddev, sep='')
