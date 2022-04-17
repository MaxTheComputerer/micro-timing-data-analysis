from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde, norm, ttest_1samp
from sklearn.mixture import GaussianMixture
from tabulate import tabulate


# Class for performing micro-timing data analysis on a piece of music
class Piece:

    # name is the name of the subfolder within data/ that the piece's .csv files are found
    # beat_divisions is a list of integers representing how many pulse units each beat in the metre can be divided into
    # mixture_metric_locations is a list of indices representing which beats should be treated as a Gaussian mixture model instead of a Normal distribution
    def __init__(self, name, beat_divisions, mixture_metric_locations=None):
        self.name = name
        self.beat_division = beat_divisions[0]
        self.beats = len(beat_divisions)
        self.pulse_units = sum(beat_divisions)
        self.mixture_metric_locations = mixture_metric_locations

    # Private method which gets the Path objects for all .csv files for this piece
    # Can be filtered by any files with a given string in them
    def _get_paths(self, filter=''):
        filename = f'*{filter}*.csv' if filter else '*.csv'
        return Path().glob(f'data/{self.name}/{filename}')

    # Private method that loads all .csv files for a piece and concatenates them into one dataframe
    # Can be filtered by any files with a given string in them
    def _load_joined(self, filter=''):
        files = self._get_paths(filter)
        self.df = pd.concat([pd.read_csv(file) for file in files])

    # Private method that loads all .csv files for a piece and returns them as a list of dataframes
    # Can be filtered by any files with a given string in them
    def _load_separately(self, filter=''):
        files = self._get_paths(filter)
        return [pd.read_csv(file) for file in files]

    # Print the piece's dataframe (or optionally, any table recognised by tabulate) to the console
    def print(self, table=None):
        if table is not None:
            print(tabulate(table, headers="keys"))
        else:
            print(tabulate(self.df, headers="keys"))

    # Loads a piece which has already been processed
    # Processed is defined as having columns for onsets, metric locations, validity, and phase of each note
    # The names of the columns representing each of these must be passed in as strings
    # Offset is calculated and it is converted to quarter lengths
    # Phase is converted to pulse units
    def load_processed(self, onset=None, cycle_num=None, metric_loc=None, metric_loc_index=None, valid=None, phase=None, filter=''):
        if onset and metric_loc and valid and phase:
            self._load_joined(filter)
            self.onset = onset
            self.cycle_num = cycle_num
            self.metric_loc = metric_loc
            self.metric_loc_index = metric_loc_index
            self.valid = valid
            self.phase = phase
            # Calculate phase in pulse units
            self.df[self.phase] = self.df[self.phase] * self.beat_division
            # Calculate offset in pulse units
            self.df['Offset_pulse_units'] = self.df[self.phase] - (self.df[self.metric_loc_index] - 1)
            # Convert offset to quarter lengths
            self.df['Offset'] = self.df['Offset_pulse_units'] / 2

            # Filter invalid or nan values
            self.df = self.df[self.df[self.valid] == 1]
            self.df = self.df[self.df[self.phase].notna()]
        else:
            print("Please provide column names for onset times, cycle numbers, metric locations, metric location indices, phase, and valid point")

    # Loads a piece which is unprocessed, i.e. only has onset values
    # Estimates metric locations and phase for data with onsets for only and all beats
    # Assumes that only onsets on exact beats are included, the first onset is the first beat, and all beats are included with no discontinuities
    def load_from_onsets(self, onset=None, filter='', dfs=None, drop=True):
        if onset:
            if dfs is None:
                dfs = self._load_separately(filter)
            for df in dfs:

                # Perform calculations to estimate phase
                df['Cycle_number'] = (df.index // self.beats) + 1
                df['Metric_location'] = df.index % self.beats

                if drop:
                    # Remove any incomplete bars from the end (apart from its first note)
                    last_loc = int(df.iloc[-1]['Metric_location'])
                    df.drop(df.tail(last_loc).index, inplace=True)

                cycle_start_index = df.index - df['Metric_location']
                cycle_end_index = (cycle_start_index + self.beats) % len(df)
                cycle_start_onset = df.iloc[cycle_start_index][onset].reset_index(drop=True)
                cycle_end_onset = df.iloc[cycle_end_index][onset].reset_index(drop=True)
                cycle_duration = cycle_end_onset - cycle_start_onset
                isochronous_beat_duration = cycle_duration / self.beats
                isochronous_onset = cycle_start_onset + (df['Metric_location'] * isochronous_beat_duration)
                offset_seconds = df[onset] - isochronous_onset
                df['Offset'] = (offset_seconds / isochronous_beat_duration) * (self.beat_division / 2)
                df['Phase'] = df['Offset'] + df['Metric_location']
                df['Is_included_in_grid'] = 1

                # Filter invalid or nan values
                df = df[df['Phase'].notna()]    

            self.df = pd.concat(dfs)

            self.onset = onset
            self.metric_loc = 'Metric_location'
            self.valid = 'Is_included_in_grid'
            self.phase = 'Phase'
            self.df_list = dfs
        else:
            print("Please provide column name for onset times")

    # Private method to use maximum likelihood estimation to fit and plot (on axis) a Normal distribution to a series
    # Optionally also resamples values from the fitted distribution and plots these
    def _plot_mle(self, series, axis, resample=False):
        x_grid = np.linspace(min(series), max(series), 1000)
        mean = series.mean()
        stddev = series.std()
        pdf = norm.pdf(x_grid, mean, stddev)
        axis.plot(x_grid, pdf, color='black', linewidth=1.0)
        if resample:
            axis.hist(np.random.normal(mean, stddev, len(series)), bins=20, density=True, stacked=True, alpha=0.5, label='MLE samples')
            axis.legend()

    # Private method to use maximum likelihood estimation to fit and plot (on axis) a Gaussian mixture model to a series
    # Suitable for data which consists of multiple Normal distribution clusters within it
    # Optionally also resamples values from the fitted distribution and plots these
    def _plot_mixture_mle(self, series, axis, components=2, resample=False):
        x_grid = np.linspace(min(series), max(series), len(series)).reshape(-1,1)
        samples = np.array(series).reshape(-1, 1)
        gm = GaussianMixture(components, covariance_type="spherical").fit(samples)
        logprob = gm.score_samples(x_grid)
        pdf = np.exp(logprob)
        axis.plot(x_grid, pdf)
        if resample:
            axis.hist(gm.sample(len(series))[0], bins=20, density=True, stacked=True, alpha=0.5, label='MLE samples')
            axis.legend()

    # Private method to use kernel density estimation to fit and plot (on axis) a custom distribution to a series
    # Suitable for data which does not fit a Normal (or any standard) distribution, or where the exact shape of the data should be preserved
    # This approach was discarded in favour of maximum likelihood estimation
    # Optionally also resamples values from the fitted distribution and plots these
    def _plot_kde(self, series, axis, resample=False):
        kde = gaussian_kde(series)
        x_grid = np.linspace(min(series), max(series), 1000)
        pdf = kde.evaluate(x_grid)
        axis.plot(x_grid, pdf)
        if resample:
            axis.hist(kde.resample(len(series)).ravel(), bins=20, density=True, stacked=True, alpha=0.5, label='KDE samples')
            axis.legend()

    # Plots a histogram of the distributions of timings for each metric location, either on separate or a combined plot
    # mle (maximum likelihood estimation) and kde (kernel density estimation) arguments being True will fit the corresponding distribution to the data and plot its PDF
    # Optionally also resamples values from the fitted distribution and plots these
    def plot_histogram(self, separately=False, mle=True, kde=False, resample=False, save_format=None, figsize=(6.5, 1.5)):
        df = self.df
        metric_locations = df[self.metric_loc].unique()
        metric_locations.sort()
        
        if separately:
            axs = df.hist('Offset', by=self.metric_loc, bins=20, density=True, stacked=True, alpha=(0.5 if resample else 0.7), layout=(len(metric_locations)//3, 3), figsize=figsize)
            if mle or kde:
                for i in range(len(metric_locations)):
                    location = metric_locations[i]
                    series = df[df[self.metric_loc] == location]['Offset']
                    if mle:
                        if self.mixture_metric_locations and location in self.mixture_metric_locations:
                            self._plot_mixture_mle(series, axs.flat[i], resample=resample)
                        else:
                            self._plot_mle(series, axs.flat[i], resample=resample)
                    if kde:
                        self._plot_kde(series, axs.flat[i], resample=resample)
                    axs.flat[i].axvline(0, color="grey", linestyle='--', linewidth=1.0, alpha=0.8)
                    axs.flat[i].set_title(f'Beat {int(location) + 1}')
                    axs.flat[i].set_xlabel('Metric event')
                    axs.flat[i].set_ylabel('Density')
        else:
            if save_format is not None:
                fig = plt.gcf()
                fig.set_size_inches(figsize)
            plt.xlabel('Metric event')
            plt.ylabel('Density')
            colour = 0
            for location in metric_locations:
                series = df[df[self.metric_loc] == location][self.phase]
                plt.hist(series, bins=20, density=True, stacked=True, alpha=(0.5 if resample else 0.7), color=f'C{colour // self.beat_division}')
                colour += 1

                loc_index = df[df[self.metric_loc] == location][self.metric_loc_index].iloc[0] - 1
                plt.axvline(loc_index, color="grey", linestyle='--', linewidth=1.0, alpha=0.8)
                
                if mle:
                    if self.mixture_metric_locations and location in self.mixture_metric_locations:
                        self._plot_mixture_mle(series, plt)
                    else:
                        self._plot_mle(series, plt)
                if kde:
                    self._plot_mle(series, plt)
            plt.xticks(np.arange(0, self.pulse_units, 1.0))
        if save_format is not None:
            plt.savefig(self.name + save_format, bbox_inches="tight")
        plt.show()

    # Prints maximum likelihood estimates of the mean and standard deviation of a fitted Normal distribution for each metric location
    # If a Gaussian mixture model was used, the component with smallest mean is chosen
    # Data is printed in a CSV-like format
    def print_mle(self):
        df = self.df
        metric_locations = df[self.metric_loc].unique()
        metric_locations.sort()

        print('Beat index,Pulse unit index,Mean,Standard deviation')
        for location in metric_locations:
            series = df[df[self.metric_loc] == location]['Offset']
            if self.mixture_metric_locations and location in self.mixture_metric_locations:
                samples = np.array(series).reshape(-1, 1)
                gm = GaussianMixture(2, covariance_type="spherical").fit(samples)
                component_index = np.argmin(gm.means_)
                mean = gm.means_[component_index][0]
                stddev = gm.covariances_[component_index]
            else:
                mean = series.mean()
                stddev = series.std()
            beat = int(np.floor(location))
            pulse_unit = int(np.rint((10/self.beat_division) * (location - beat)))
            print(beat,',',pulse_unit,',',mean,',',stddev, sep='')

    # Private method for evaluating a general natural logarithmic function
    def _logf(self, x, a, b, c):
        return a * np.log(x + b) + c

    # Private method for evaluating a general quadratic function
    def _quadraticf(self, x, a, b, c):
        return (a * (x**2)) + (b * x) + c

    # Private method for evaluating a general logarithmic function below tempo_cutoff, and a general quadratic function above
    def _combinedf(self, x, a, b, c, d, e, f):
        return np.where(x < self.tempo_cutoff, self._logf(x,a,b,c), self._quadraticf(x,d,e,f))

    # Tempo analysis for Jembe music
    # Analyses the changing tempo according to beat_instrument, which is any instrument which plays on each beat (often Jembe 2)
    # Assumes tempo can be modelled as roughly logarithmic until tempo_cutoff %, after which it is quadratic
    # i.e. y = a log(x+b) + c for x < tempo_cutoff, and y = dx^2 + ex + f for x >= tempo_cutoff
    # Plots tempo curve for each take and the average tempo, fits curves to the average tempo and plots them, and prints parameters
    # Tempo is averaged with a sliding window of size 10
    # Also calculates and prints average duration of the piece across all takes
    def tempo(self, beat_instrument, tempo_cutoff, save_format=None, figsize=(6,4)):
        dfs = self._load_separately(beat_instrument)
        self.tempo_cutoff = tempo_cutoff
        dfs_new = []
        for df in dfs:
            df.drop(df[df[self.valid] != 1].index, inplace=True)
            # Filter to just beats
            df.drop(df[~df[self.metric_loc].isin(np.arange(self.beats))].index, inplace=True)
            # Redefine Onset_time column to allow shift
            df['Onset_time'] = df[self.onset]
            df['Tempo'] = 60 / (df.Onset_time - df.Onset_time.shift(1))
            first_onset = df[self.onset].iloc[0]
            last_onset = df[self.onset].iloc[-1]
            duration = last_onset - first_onset
            df['Duration'] = duration
            # Percentage progress throughout the piece
            progress = ((df[self.onset] - first_onset) / duration) * 100
            df['Progress'] = progress.round(1)
            df = df.groupby(['Progress'], as_index=False).mean()
            df['Average Tempo'] = df['Tempo'].rolling(window=10).mean()
            plt.plot(df['Progress'], df['Average Tempo'], linewidth=0.5, alpha=0.5, color='gray')
            dfs_new.append(df)
        df = pd.concat(dfs_new)

        m = df.groupby(['Progress'], as_index=False).mean()
        m['Average Tempo'] = m['Tempo'].rolling(window=10).mean()
        m['Tempo stddev'] = m['Tempo'].rolling(window=10).std()
        plt.plot(m['Progress'], m['Average Tempo'])
        plt.fill_between(m['Progress'], m['Average Tempo'] - m['Tempo stddev'], m['Average Tempo'] + m['Tempo stddev'], color='C0', alpha=0.2)

        m = m.dropna()
        popt,_ = curve_fit(self._combinedf, m['Progress'], m['Average Tempo'])
        a,b,c,d,e,f = popt
        print('Params:')
        print('a =', a)
        print('b =', b)
        print('c =', c)
        print('d =', d)
        print('e =', e)
        print('f =', f)
        plt.plot(m['Progress'], self._combinedf(m['Progress'],a,b,c,d,e,f), color='black')

        dur = df['Duration'].unique()
        print('Mean duration:', dur.mean())
        
        plt.xlabel('Relative position in the piece (%)')
        plt.ylabel('Tempo (bpm)')

        if save_format is not None:
            fig = plt.gcf()
            fig.set_size_inches(figsize)
            plt.savefig(self.name + '-tempo' + save_format, bbox_inches="tight")
        plt.show()


    # Analyses the rhythm patterns for a given instrument and generates a random sequence of cycles according to cycle transition probabilities
    # If int_output is True, the output will be a list of integers. Each integer's binary expansion corresponds to which metrical locations are onsets
    # Otherwise, the output will be a list of lists
    def rhythm_sequence(self, instrument, num_of_samples, int_output=False):
        dfs = self._load_separately(instrument)
        cycle_onsets = []
        starting_cycles = []

        for df in dfs:
            df.drop(df[df[self.valid] != 1].index, inplace=True)
            df.drop(df[df[self.phase].isna()].index, inplace=True)
            cycles = df[self.cycle_num].unique()
            first = True
            for cycle in cycles:
                onsets = []
                locs = df[df[self.cycle_num] == cycle][self.metric_loc_index].unique()
                for i in range(self.pulse_units):
                    # Record whether there is an onset at this position in this cycle
                    is_played = 1 if i+1 in locs else 0
                    onsets.append(is_played)

                # Convert list of 1s and 0s to an integer
                number = int("".join(str(i) for i in onsets),2)
                cycle_onsets.append(number)
                if first:
                    starting_cycles.append(number)
                first = False

        # Count transitions between cycles
        trans_counts = {}
        for i in range(len(cycle_onsets)-1):
            num = cycle_onsets[i]
            next = cycle_onsets[i+1]
            if num not in trans_counts:
                trans_counts[num] = {}
            if next not in trans_counts[num]:
                trans_counts[num][next] = 0
            trans_counts[num][next] += 1

        # Calculate transition probabilities
        trans_probs = {}
        for (k,v) in trans_counts.items():
            trans_probs[k] = {k1: v1 / sum(v.values()) for k1, v1 in v.items()}

        # Helper function to take an integer and return its binary expansion as a list
        def to_binary(n):
            return [int(x) for x in bin(n)[2:].zfill(self.pulse_units)]

        # Generate random sequence of cycles
        num = np.random.choice(starting_cycles)
        if int_output:
            nums = [num]
        else:
            nums = [to_binary(num)]
        for i in range(num_of_samples):
            probs = trans_probs[num]
            next = np.random.choice(list(probs.keys()), p=list(probs.values()))
            if int_output:
                nums.append(next)
            else:
                nums.append(to_binary(next))
            num = next
        return nums

    # Performs a one-sample t-test on a given metric location to determine if there is significant micro-timing in the data
    # Tests if the sample mean is significantly different from the population mean of 0
    # Plots a histogram for each piece in the dataset, and prints their p-values, means, and if it was significant or not
    def statistical_test(self, test_metric_location, significance=0.05, filter=''):
        dfs = self.df_list
        dfs_new = []
        file_paths = list(self._get_paths(filter))
        i = 0

        for df in dfs:
            piece_name = file_paths[i].stem
            df['Piece'] = piece_name
            df_filtered = df[(df['Metric_location'] == test_metric_location) & (df['Phase'] < test_metric_location + 1)]
            offsets_filtered = df_filtered['Offset']

            # one-sample t-test
            _, p_value = ttest_1samp(offsets_filtered, popmean=0)
            sample_mean = offsets_filtered.mean()

            df['p_value'] = p_value
            df_filtered = df[(df['Metric_location'] == test_metric_location) & (df['Phase'] < test_metric_location + 1)]

            dfs_new.append(df_filtered)
            print(f'{i} - {piece_name}: p={p_value}, mean={sample_mean}, significant={p_value < significance}')
            i += 1
            
        df_all = pd.concat(dfs_new)
        df_all.hist('Offset', by='Piece', bins=10, density=True, stacked=True)
        plt.show()

def enable_latex_output():
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })

def disable_latex_output():
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({
        "pgf.texsystem": "xelatex",
        'font.family': 'sans-serif',
        'text.usetex': False,
        'pgf.rcfonts': True,
    })
