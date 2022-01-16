import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde, norm
from pathlib import Path

from config import *

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
    files = Path().glob(f'data/{NAME}/*.csv')
    df = pd.concat([pd.read_csv(file) for file in files])
    df = df[df[VALID] == 1]
    df = df[df[PHASE].notna()]
    df['Offset'] = (df[PHASE] - df[METRIC_LOC]) * 3
    metric_locations = df[METRIC_LOC].unique()
    metric_locations.sort()

    axs = df.hist('Offset', by=METRIC_LOC, bins=20, density=True, stacked=True, alpha=0.5, label='data')

    for i in range(len(metric_locations)):
        location = metric_locations[i]
        series = df[df[METRIC_LOC] == location]['Offset']
        plot_mle(series, axs.flat[i], resample=True)
    plt.show()

def plot_together():
    files = Path().glob(f'data/{NAME}/*.csv')
    df = pd.concat([pd.read_csv(file) for file in files])
    df = df[df[VALID] == 1]
    df = df[df[PHASE].notna()]
    df[PHASE] = 3 * df[PHASE]
    metric_locations = df[METRIC_LOC].unique()
    metric_locations.sort()

    for location in metric_locations:
        series = df[df[METRIC_LOC] == location][PHASE]
        plt.hist(series, bins=20, density=True, stacked=True, alpha=0.5, label='data')
        plot_mle(series, plt)
    plt.xticks(np.arange(0, 12, 1.0))
    plt.show()

plot_together()
