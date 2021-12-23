import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde, norm
from pathlib import Path

def plot_kde(series, axis, resample=False):
    kde = gaussian_kde(series)
    x_grid = np.linspace(min(series), max(series), 1000)
    pdf = kde.evaluate(x_grid)
    axis.plot(x_grid, pdf)
    if resample:
        axis.hist(kde.resample(len(series)).ravel(), bins=20, density=True, stacked=True, alpha=0.5, label='kde samples')
        axis.legend()

def plot_mle(series, axis, resample=False):
    x_grid = np.linspace(min(series), max(series), 1000)
    mean = series.mean()
    stddev = series.std()
    pdf = norm.pdf(x_grid, mean, stddev)
    axis.plot(x_grid, pdf)
    if resample:
        axis.hist(np.random.normal(mean, stddev, len(series)), bins=20, density=True, stacked=True, alpha=0.5, label='mle samples')
        axis.legend()

def plot_separately():
    files = Path().glob(f'data/*.csv')
    df = pd.concat([pd.read_csv(file) for file in files])
    df = df[df['Is_included_in_grid'] == 1]
    df = df[df['Phase'].notna()]
    df['Offset'] = (df['Phase'] - df['Metric_location']) * 3
    metric_locations = df['Metric_location'].unique()
    metric_locations.sort()

    axs = df.hist('Offset', by='Metric_location', bins=20, density=True, stacked=True, alpha=0.5, label='data')

    for i in range(len(metric_locations)):
        location = metric_locations[i]
        series = df[df['Metric_location'] == location]['Offset']
        plot_mle(series, axs.flat[i], resample=True)
        #plot_kde(series, axs.flat[i], resample=False)
    plt.show()

def plot_together():
    files = Path().glob(f'data/*.csv')
    df = pd.concat([pd.read_csv(file) for file in files])
    df = df[df['Is_included_in_grid'] == 1]
    df = df[df['Phase'].notna()]
    df['Phase'] = 3 * df['Phase']
    metric_locations = df['Metric_location'].unique()
    metric_locations.sort()

    for location in metric_locations:
        series = df[df['Metric_location'] == location]['Phase']
        plt.hist(series, bins=20, density=True, stacked=True, alpha=0.5, label='data')
        plot_mle(series, plt)
        #plot_kde(series, plt)
    plt.xticks(np.arange(0, 12, 1.0))
    plt.show()

plot_separately()
