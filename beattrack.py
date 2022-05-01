# Use FMP to estimate locations of beats for waltz
# Usage: python beattrack.py <path_to_audio> <tempo_estimate>
# Adapted from https://www.audiolabs-erlangen.de/resources/MIR/FMP/C6/C6S3_BeatTracking.html

import sys
from pathlib import Path

import libfmp.c6
import librosa
import numpy as np

def convert_tempo(tempo):
  return (1/tempo) * 60 * 100

audio_path = Path(sys.argv[1])
title = audio_path.stem
tempo_est = int(sys.argv[2])

samplerate = 22050
penalty_factor = 0.5

audio_series, _ = librosa.load(str(audio_path), samplerate)

novelty_function, feature_rate = libfmp.c6.compute_novelty_spectrum(audio_series, Fs=samplerate, N=2048, H=512, gamma=100, M=10, norm=True)
novelty_function, feature_rate = libfmp.c6.resample_signal(novelty_function, Fs_in=feature_rate, Fs_out=100)

beat_sequence_samples = libfmp.c6.compute_beat_sequence(novelty_function, convert_tempo(tempo_est), factor=penalty_factor)
sample_times = np.arange(novelty_function.shape[0]) / feature_rate

beats_sequence_seconds = sample_times[beat_sequence_samples]

output_path = Path() / 'data' / 'waltz-auto' / (title + '.txt')
np.savetxt(output_path, beats_sequence_seconds)
print('Saved to', str(output_path.resolve()))
