from piece import *

suku = Piece('suku', [3,3,3,3])
suku.load_processed('Onset_time', 'Cycle_number', 'Metric_location', 'Metric_location_index', 'Is_included_in_grid', 'Phase')

manjanin = Piece('manjanin', [3,3,3,3])
manjanin.load_processed('onsets_time', 'cycle', 'subdivision', 'subdivision_index', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

maraka = Piece('maraka', [3,3,3,3])
maraka.load_processed('onsets_time', 'cycle', 'subdivision', 'subdivision_index', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

woloso = Piece('woloso', [3,3,3,3])
woloso.load_processed('onsets_time', 'cycle', 'subdivision', 'subdivision_index', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

blue_danube = Piece('blue-danube', [2,2,2], [1])
blue_danube.load_from_onsets('TIME')

waltz_auto = Piece('waltz-auto', [2,2,2])
waltz_auto.load_from_onsets('Onset')

waltz_manual = Piece('waltz-manual', [2,2,2])
waltz_manual.load_from_onsets('Onset')

# Suku
def suku_plot():
    suku.plot_histogram()

def suku_save():
    enable_latex_output()
    suku.plot_histogram('.pgf')
    disable_latex_output()
    suku.plot_histogram()

def suku_tempo():
    suku.tempo('Jembe-2', 95)

def suku_tempo_save():
    enable_latex_output()
    suku.tempo('Jembe-2', 95, save_format='.pgf')
    disable_latex_output()
    suku.tempo('Jembe-2', 95)

def suku_mle():
    suku.print_mle()

def suku_rhythm(num_of_samples, int_output=True, instrument='Jembe-1'):
    print(suku.rhythm_sequence(instrument, num_of_samples, int_output))


# Manjanin
def manjanin_plot():
    manjanin.plot_histogram()

def manjanin_tempo():
    manjanin.tempo('Jembe2', 95.5)

def manjanin_tempo_save():
    enable_latex_output()
    manjanin.tempo('Jembe2', 95.5, save_format='.pgf')
    disable_latex_output()
    manjanin.tempo('Jembe2', 95.5)

def manjanin_mle():
    manjanin.print_mle()

def manjanin_rhythm(num_of_samples, int_output=True, instrument='Jembe1'):
    print(manjanin.rhythm_sequence(instrument, num_of_samples, int_output))


# Maraka
def maraka_plot():
    maraka.plot_histogram()

def maraka_tempo():
    maraka.tempo('Jembe2', 93)

def maraka_mle():
    maraka.print_mle()

def maraka_rhythm(num_of_samples, int_output=True, instrument='Jembe1'):
    print(maraka.rhythm_sequence(instrument, num_of_samples, int_output))


# Woloso
def woloso_plot():
    woloso.plot_histogram()

def woloso_tempo():
    woloso.tempo('Jembe2', 75)

def woloso_mle():
    woloso.print_mle()

def woloso_rhythm(num_of_samples, int_output=True, instrument='Jembe1'):
    print(woloso.rhythm_sequence(instrument, num_of_samples, int_output))


# Blue Danube
def blue_danube_plot():
    blue_danube.plot_histogram(separately=True)

def blue_danube_mle():
    blue_danube.print_mle()


# Waltz (automatic beat tracking)
def waltz_auto_plot():
    waltz_auto.plot_histogram(separately=True)

def waltz_auto_save():
    enable_latex_output()
    waltz_auto.plot_histogram(separately=True, save_format='.pgf', figsize=(6.5,2))
    disable_latex_output()
    waltz_auto.plot_histogram(separately=True, figsize=(6.5,2))

def waltz_auto_mle():
    waltz_auto.print_mle()

def waltz_auto_stats():
    waltz_auto.statistical_test(1)


# Waltz (manual beat tracking)
def waltz_manual_plot():
    waltz_manual.plot_histogram(separately=True)

def waltz_manual_mle():
    waltz_manual.print_mle()

def waltz_manual_stats():
    waltz_manual.statistical_test(1)
