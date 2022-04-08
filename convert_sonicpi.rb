require_relative "metre"

def in_thread(&block)
    $output += "part = stream.Part()\n"
    block.call
    $output += "score.append(part)\n"
end

def parse_metre_tree(sequence)
    if sequence.is_a?(MetreTree)
        ms = "meter.MeterSequence(["
        ms += sequence.sequence.map{ |m| parse_metre_tree(m) }.join(',')
        ms += "])"
        return ms
    else
        return "meter.MeterTerminal('#{sequence.fraction.numerator}/#{sequence.fraction.denominator}')"
    end
end

def use_metre(list)
    $metre = Metre.new(list)
    $new_metre = true
end

def use_bpm(tempo)
    $output += "measure.append(tempo.MetronomeMark(number=#{tempo}, referent=#{$metre.beat_duration}))\n"
end

def add_note(n, level, duration)
    quarter_length = $metre.get_level(level).offset_to_quarter_length($offset) * duration
    if n.is_a?(Array)
        # Chord
        pitches = n.map{|n| n.to_s}.to_s
        pitches.gsub!('s','#')
        pitches.gsub!('b','-')
        $output += "n = chord.Chord(#{pitches})\n"
    else
        # Note
        pitch = n.to_s
        pitch.gsub!('s','#')
        pitch.gsub!('b','-')
        $output += "n = note.Note('#{pitch}')\n"
    end
    $output += "n.duration.quarterLength = #{quarter_length}\n"
    $output += "measure.append(n)\n"
    $offset += quarter_length
end

def add_rest(level, duration)
    quarter_length = $metre.get_level(level).offset_to_quarter_length($offset) * duration
    $output += "r = note.Rest(quarterLength=#{quarter_length})\n"
    $output += "measure.append(r)\n"
    $offset += quarter_length
end

def bar(&block)
    $output += "measure = stream.Measure()\n"
    $offset = 0
    block.call
    if $new_metre and $offset > 0
        $output += "ts = measure.bestTimeSignature()\n"
        $output += "ts.beatSequence = #{parse_metre_tree($metre)}\n"
        $output += "measure.insert(0, ts)\n"
        $new_metre = false
    end
    $output += "part.append(measure)\n"
end

$output = "from music21 import *\n\n"
$output += "score = stream.Score()\n"

require_relative ARGV[0]

$output += "score.metadata = metadata.Metadata(title='#{$title}')\n"
$output += "score.show()\n"

puts $output

if ARGV.include?("-s")
    path = File.dirname(ARGV[0]) + "\\" + File.basename(ARGV[0], ".*") + ".py"
    File.open(path, "w") { |f| f.write $output}
    puts "Saved to #{path}"
end
