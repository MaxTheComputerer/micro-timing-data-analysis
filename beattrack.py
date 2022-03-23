# Use FMP to estimate locations of beats for waltz
# Usage: python beattrack.py <path_to_audio> <tempo_estimate>

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

x, Fs = librosa.load(str(audio_path), samplerate)

nov, Fs_nov = libfmp.c6.compute_novelty_spectrum(x, Fs=samplerate, N=2048, H=512, gamma=100, M=10, norm=True)
nov, Fs_nov = libfmp.c6.resample_signal(nov, Fs_in=Fs_nov, Fs_out=100)

B = libfmp.c6.compute_beat_sequence(nov, convert_tempo(tempo_est), factor=penalty_factor)
T_coef = np.arange(nov.shape[0]) / Fs_nov
beats_sec = T_coef[B]

output_path = Path() / 'data' / 'waltz-auto' / (title + '.txt')
np.savetxt(output_path, beats_sec)
print('Saved to', str(output_path.resolve()))
