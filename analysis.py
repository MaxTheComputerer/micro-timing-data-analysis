from piece import Piece

suku = Piece('suku', [3,3,3,3])
suku.load_processed('Onset_time', 'Metric_location', 'Is_included_in_grid', 'Phase')

manjanin = Piece('manjanin', [3,3,3,3])
manjanin.load_processed('onsets_time', 'subdivision', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

maraka = Piece('maraka', [3,3,3,3])
maraka.load_processed('onsets_time', 'subdivision', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

woloso = Piece('woloso', [3,3,3,3])
woloso.load_processed('onsets_time', 'subdivision', 'is_valid_subdivision_assignment', 'relative_location_within_the_cycle_democratic')

blue_danube_processed = Piece('blue-danube', [2,2,2], [1])
blue_danube_processed.load_processed('Onset_time', 'Metric_location', 'Is_included_in_grid', 'Phase')

blue_danube_unprocessed = Piece('blue-danube-unprocessed', [2,2,2], [1])
blue_danube_unprocessed.load_from_onsets('TIME')

# Suku
def suku_plot():
    suku.plot_histogram()

def suku_tempo():
    suku.tempo('Jembe-2', 95)

def suku_mle():
    suku.print_mle()


# Manjanin
def manjanin_plot():
    manjanin.plot_histogram()

def manjanin_tempo():
    manjanin.tempo('Jembe2', 95.5)

def manjanin_mle():
    manjanin.print_mle()


# Maraka
def maraka_plot():
    maraka.plot_histogram()

def maraka_tempo():
    maraka.tempo('Jembe2', 93)

def maraka_mle():
    maraka.print_mle()


# Woloso
def woloso_plot():
    woloso.plot_histogram()

def woloso_tempo():
    woloso.tempo('Jembe2', 75)

def woloso_mle():
    woloso.print_mle()


# Blue Danube
def blue_danube_plot():
    blue_danube_processed.plot_histogram(separately=True)

def blue_danube_mle():
    blue_danube_processed.print_mle()


# Blue Danube (unprocessed)
def blue_danube_unprocessed_plot():
    blue_danube_unprocessed.plot_histogram(separately=True)

def blue_danube_unprocessed_mle():
    blue_danube_unprocessed.print_mle()
