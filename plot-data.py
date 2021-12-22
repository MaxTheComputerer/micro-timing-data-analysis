import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from tabulate import tabulate
from pathlib import Path

instruments = ['Dundun-1']

def plot_kde(series, axis, resample=True, legend=True):
    kde = gaussian_kde(series)
    x_grid = np.linspace(min(series), max(series), 1000)
    pdf = kde.evaluate(x_grid)
    #axis.plot(x_grid, pdf)
    if resample:
        axis.hist(kde.resample(len(series)).ravel(), bins=20, density=True, stacked=True, alpha=0.5, label='samples')
    if legend:
        axis.legend()

def plot_separately():
    for instrument in instruments:
        files = Path().glob(f'data/*{instrument}.csv')
        df = pd.concat([pd.read_csv(file) for file in files])
        df = df[df['Is_included_in_grid'] == 1]
        df = df[df['Phase'].notna()]
        df['Offset'] = df['Phase'] - df['Metric_location']
        metric_locations = df['Metric_location'].unique()
        metric_locations.sort()

        axs = df.hist('Offset', by='Metric_location', bins=20, density=True, stacked=True, alpha=0.5, label='data')

        for i in range(len(metric_locations)):
            location = metric_locations[i]
            series = df[df['Metric_location'] == location]['Offset']
            plot_kde(series, axs.flat[i])
        plt.show()

def plot_together():
    for instrument in instruments:
        files = Path().glob(f'data/*.csv')
        df = pd.concat([pd.read_csv(file) for file in files])
        df = df[df['Is_included_in_grid'] == 1]
        df = df[df['Phase'].notna()]
        metric_locations = df['Metric_location'].unique()
        metric_locations.sort()

        for location in metric_locations:
            series = df[df['Metric_location'] == location]['Phase']
            plt.hist(series, bins=20, density=True, stacked=True, alpha=0.5, label='data')
            plot_kde(series, plt, resample=False, legend=False)
        plt.show()

plot_together()
