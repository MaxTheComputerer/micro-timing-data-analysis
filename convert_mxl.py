import math
import sys
from fractions import Fraction
from pathlib import Path

from music21 import chord, converter, meter, note


class MXLConverter:

    def load_xml(self, path):
        return converter.parse(path)

    def convert_duration(self, note):
        beat_sequence = self.time_signature.beatSequence
        indices = beat_sequence.offsetToAddress(note.offset)
        level = duration = None
        for i in range(len(indices)):
            # Try to find a level which the note's duration can be divided into
            subsequence = beat_sequence[indices[i]]
            if note.quarterLength % subsequence.duration.quarterLength == 0:
                level = i
                duration = int(note.quarterLength / subsequence.duration.quarterLength)
                break
            beat_sequence = subsequence
        if level is None:
            # Need to go deeper
            note_fraction = Fraction(note.quarterLength) / 4
            deepest_level = Fraction(beat_sequence.numerator, beat_sequence.denominator)
            level_difference = math.log(note_fraction.denominator / deepest_level.denominator, 2)
            level = int(len(indices) + level_difference - 1)
            duration = note_fraction.numerator
            if deepest_level.numerator != 1:
                level += 1
                duration *= 2
        return (level, duration)

    def convert_note(self, note):
        pitch = note.nameWithOctave.replace('#','s').replace('-','b')
        level, duration = self.convert_duration(note)
        return f'add_note :{pitch}, {level}, {duration}\n'

    def convert_rest(self, rest):
        level, duration = self.convert_duration(rest)
        return f'add_rest {level}, {duration}\n'

    def convert_chord(self, chord):
        level, duration = self.convert_duration(chord)
        pitches = str([f":{p.nameWithOctave.replace('#','s').replace('-','b')}" for p in chord.pitches]).replace("\'", "")
        return f'add_note {pitches}, {level}, {duration}\n'

    def convert_tempo(self, tempo):
        return f'use_bpm {tempo.number}\n'

    def convert_measure(self, measure):
        output = 'bar do\n'
        for element in measure.getElementsByClass(['Note', 'Rest', 'Chord', 'MetronomeMark']):
            if isinstance(element, note.Note):
                output += self.convert_note(element)
            elif isinstance(element, note.Rest):
                output += self.convert_rest(element)
            elif isinstance(element, chord.Chord):
                output += self.convert_chord(element)
            else:
                output += self.convert_tempo(element)
        output += 'end\n'
        return output

    def parse_meter_sequence(self, sequence):
        if isinstance(sequence, meter.MeterSequence):
            return f'[{",".join([self.parse_meter_sequence(i) for i in sequence])}]'
        else:
            # MeterTerminal
            return f'{sequence.numerator}/{sequence.denominator}r'
            

    def convert_metre(self, beat_sequence):
        return f'use_metre {self.parse_meter_sequence(beat_sequence)}\n'

    def convert_part(self, part):
        output = 'in_thread do\n'
        for measure in part['Measure']:
            if measure.timeSignature is not None:
                self.time_signature = measure.timeSignature
                output += self.convert_metre(measure.timeSignature.beatSequence)
            output += self.convert_measure(measure)
        output += 'end\n'
        return output

    def convert_score(self, score):
        output = f'$title = "{score.metadata.title}"\n'
        for part in score.parts:
            output += self.convert_part(part)
        return output


if __name__ == "__main__":
    path = Path(sys.argv[1])
    mxlconverter = MXLConverter()
    score = mxlconverter.load_xml(path)
    converted = mxlconverter.convert_score(score)
    print(converted)
    if '--no-save' not in sys.argv:
        with open(path.parent / (path.stem + '.rb'), 'w') as file:
            file.write(converted)
        print(f"Saved to {path.parent / (path.stem + '.rb')}")
