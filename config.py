NAME = 'woloso'

if NAME == 'suku':
    ONSET = 'Onset_time'
    VALID = 'Is_included_in_grid'
    METRIC_LOC = 'Metric_location'
    PHASE = 'Phase'
    JEMBE2 = 'Jembe-2'
    TEMPO_CUTOFF = 95
else:
    ONSET = 'onsets_time'
    VALID = 'is_valid_subdivision_assignment'
    METRIC_LOC = 'subdivision'
    PHASE = 'relative_location_within_the_cycle_democratic'
    JEMBE2 = 'Jembe2'

    if NAME == 'manjanin':
        TEMPO_CUTOFF = 95.5
    elif NAME == 'maraka':
        TEMPO_CUTOFF = 93
    elif NAME == 'woloso':
        TEMPO_CUTOFF = 75
