# Convert a transcription of a jembe-1 part into Sonic Pi code

from pathlib import Path
import sys

piece = sys.argv[1]
path = Path(f'data/{piece}')
with open(path / "transcription.txt", 'r') as file:
    lines = file.read().splitlines()

def make_bar(bar):
    symbol_lookup = {'t': 'Tone', 's': 'Slap', 'b': 'Bass'}
    new_bar = "use_bpm get[:tempo]\nbar do\n"
    for symbol in bar:
        if symbol == '.':
            new_bar += "add_rest -1\n"
        elif len(symbol) == 1:
            new_bar += "jembe1 '" + symbol_lookup[symbol] + "'\n"
        elif len(symbol) == 2:
            for s in list(symbol):
                new_bar += "jembe1 '" + symbol_lookup[s] + "', -2\n"
        else:
            raise ValueError("Unrecognised symbol")
    new_bar += "end\n"
    return new_bar

output = ""
for line in lines:
    line = line.split(' ')
    bar1 = line[:12]
    bar2 = line[:12]
    output += make_bar(bar1) + make_bar(bar2)

with open(path / "transcription.rb", 'w') as out_file:
    out_file.write(output)

print("File converted")
