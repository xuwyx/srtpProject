import midi
import os
import math
import pickle as pkl
import numpy as np

# INDICES IN BATCHES (LENGTH,FREQ,VELOCITY are repeated self.tones_per_cell times):
TICKS_FROM_PREV_START = 0
LENGTH = 1
FREQ = 2
VELOCITY = 3
tones_per_cell = 1

# INDICES IN SONG DATA (NOT YET BATCHED):
BEGIN_TICK = 0

NUM_FEATURES_PER_TONE = 3

output_ticks_per_quarter_note = 384.0


def read_one_file(path, filename, pace_events):
    print('Reading {}'.format(os.path.join(path, filename)))
    midi_pattern = midi.read_midifile(os.path.join(path, filename))

    #
    # Interpreting the midi pattern.
    # A pattern has a list of tracks
    # (midi.Track()).
    # Each track is a list of events:
    #   * midi.events.SetTempoEvent: tick, data([int, int, int])
    #     (The three ints are really three bytes representing one integer.)
    #   * midi.events.TimeSignatureEvent: tick, data([int, int, int, int])
    #     (ignored)
    #   * midi.events.KeySignatureEvent: tick, data([int, int])
    #     (ignored)
    #   * midi.events.MarkerEvent: tick, text, data
    #   * midi.events.PortEvent: tick(int), data
    #   * midi.events.TrackNameEvent: tick(int), text(string), data([ints])
    #   * midi.events.ProgramChangeEvent: tick, channel, data
    #   * midi.events.ControlChangeEvent: tick, channel, data
    #   * midi.events.PitchWheelEvent: tick, data(two bytes, 14 bits)
    #
    #   * midi.events.NoteOnEvent:  tick(int), channel(int), data([int,int]))
    #     - data[0] is the note (0-127)
    #     - data[1] is the velocity.
    #     - if velocity is 0, this is equivalent of a midi.NoteOffEvent
    #   * midi.events.NoteOffEvent: tick(int), channel(int), data([int,int]))
    #
    #   * midi.events.EndOfTrackEvent: tick(int), data()
    #
    # Ticks are relative.
    #
    # Tempo are in microseconds/quarter note.
    #
    # This interpretation was done after reading
    # http://electronicmusic.wikia.com/wiki/Velocity
    # http://faydoc.tripod.com/formats/mid.htm
    # http://www.lastrayofhope.co.uk/2009/12/23/midi-delta-time-ticks-to-seconds/2/
    # and looking at some files. It will hopefully be enough
    # for the use in this project.
    #
    # We'll save the data intermediately with a dict representing each tone.
    # The dicts we put into a list. Times are microseconds.
    # Keys: 'freq', 'velocity', 'begin-tick', 'tick-length'
    #
    # 'Output ticks resolution' are fixed at a 32th note,
    #   - so 8 ticks per quarter note.
    #
    # This approach means that we do not currently support
    #   tempo change events.
    #
    # TODO 1: Figure out pitch.
    # TODO 2: Figure out different channels and instruments.
    #

    song_data = []

    # Tempo:
    ticks_per_quarter_note = float(midi_pattern.resolution)
    # print('Resoluton: {}'.format(ticks_per_quarter_note))
    input_ticks_per_output_tick = ticks_per_quarter_note / output_ticks_per_quarter_note
    # if debug == 'overfit': input_ticks_per_output_tick = 1.0

    # Multiply with output_ticks_pr_input_tick for output ticks.
    for track in midi_pattern:
        last_event_input_tick = 0
        not_closed_notes = []
        for event in track:
            if type(event) == midi.events.SetTempoEvent:
                pass  # These are currently ignored
            elif (type(event) == midi.events.NoteOffEvent) or \
                    (type(event) == midi.events.NoteOnEvent and \
                                 event.velocity == 0):
                retained_not_closed_notes = []
                for e in not_closed_notes:
                    if tone_to_freq(event.data[0]) == e[FREQ]:
                        event_abs_tick = float(event.tick + last_event_input_tick) / input_ticks_per_output_tick
                        # current_note['length'] = float(ticks*microseconds_per_tick)
                        e[LENGTH] = event_abs_tick - e[BEGIN_TICK]
                        song_data.append(e)
                    else:
                        retained_not_closed_notes.append(e)
                # if len(not_closed_notes) == len(retained_not_closed_notes):
                #  print('Warning. NoteOffEvent, but len(not_closed_notes)({}) == len(retained_not_closed_notes)({})'.format(len(not_closed_notes), len(retained_not_closed_notes)))
                #  print('NoteOff: {}'.format(tone_to_freq(event.data[0])))
                #  print('not closed: {}'.format(not_closed_notes))
                not_closed_notes = retained_not_closed_notes
            elif type(event) == midi.events.NoteOnEvent:
                begin_tick = float(event.tick + last_event_input_tick) / input_ticks_per_output_tick
                note = [0.0] * (NUM_FEATURES_PER_TONE + 1)
                note[FREQ] = tone_to_freq(event.data[0])
                note[VELOCITY] = float(event.data[1])
                note[BEGIN_TICK] = begin_tick
                not_closed_notes.append(note)
                # not_closed_notes.append([0.0, tone_to_freq(event.data[0]), velocity, begin_tick, event.channel])
            last_event_input_tick += event.tick
        for e in not_closed_notes:
            # print('Warning: found no NoteOffEvent for this note. Will close it. {}'.format(e))
            e[LENGTH] = float(ticks_per_quarter_note) / input_ticks_per_output_tick
            song_data.append(e)
    song_data.sort(key=lambda e: e[BEGIN_TICK])
    if (pace_events):
        pace_event_list = []
        pace_tick = 0.0
        song_tick_length = song_data[-1][BEGIN_TICK] + song_data[-1][LENGTH]
        while pace_tick < song_tick_length:
            song_data.append([0.0, 440.0, 0.0, pace_tick, 0.0])
            pace_tick += float(ticks_per_quarter_note) / input_ticks_per_output_tick
        song_data.sort(key=lambda e: e[BEGIN_TICK])
    song_data.sort(key=lambda e: e[BEGIN_TICK])
    return song_data


def tone_to_freq(tone):
    """
      returns the frequency of a tone.

      formulas from
        * https://en.wikipedia.org/wiki/MIDI_Tuning_Standard
        * https://en.wikipedia.org/wiki/Cent_(music)
    """
    return math.pow(2, ((float(tone) - 69.0) / 12.0)) * 440.0


# def get_midi_pattern(song_data, b):
#     """
#     get_midi_pattern takes a song in internal representation
#     (a tensor of dimensions [songlength, self.num_song_features]).
#     the three values are length, frequency, velocity.
#     if velocity of a frame is zero, no midi event will be
#     triggered at that frame.
#
#     returns the midi_pattern.
#
#     Can be used with filename == None. Then nothing is saved, but only returned.
#     """
#     print('song_data[0:10]: {}'.format(song_data[0:10]))
#
#     #
#     # Interpreting the midi pattern.
#     # A pattern has a list of tracks
#     # (midi.Track()).
#     # Each track is a list of events:
#     #   * midi.events.SetTempoEvent: tick, data([int, int, int])
#     #     (The three ints are really three bytes representing one integer.)
#     #   * midi.events.TimeSignatureEvent: tick, data([int, int, int, int])
#     #     (ignored)
#     #   * midi.events.KeySignatureEvent: tick, data([int, int])
#     #     (ignored)
#     #   * midi.events.MarkerEvent: tick, text, data
#     #   * midi.events.PortEvent: tick(int), data
#     #   * midi.events.TrackNameEvent: tick(int), text(string), data([ints])
#     #   * midi.events.ProgramChangeEvent: tick, channel, data
#     #   * midi.events.ControlChangeEvent: tick, channel, data
#     #   * midi.events.PitchWheelEvent: tick, data(two bytes, 14 bits)
#     #
#     #   * midi.events.NoteOnEvent:  tick(int), channel(int), data([int,int]))
#     #     - data[0] is the note (0-127)
#     #     - data[1] is the velocity.
#     #     - if velocity is 0, this is equivalent of a midi.NoteOffEvent
#     #   * midi.events.NoteOffEvent: tick(int), channel(int), data([int,int]))
#     #
#     #   * midi.events.EndOfTrackEvent: tick(int), data()
#     #
#     # Ticks are relative.
#     #
#     # Tempo are in microseconds/quarter note.
#     #
#     # This interpretation was done after reading
#     # http://electronicmusic.wikia.com/wiki/Velocity
#     # http://faydoc.tripod.com/formats/mid.htm
#     # http://www.lastrayofhope.co.uk/2009/12/23/midi-delta-time-ticks-to-seconds/2/
#     # and looking at some files. It will hopefully be enough
#     # for the use in this project.
#     #
#     # This approach means that we do not currently support
#     #   tempo change events.
#     #
#
#     # Tempo:
#     # Multiply with output_ticks_pr_input_tick for output ticks.
#     midi_pattern = midi.Pattern([], resolution=int(output_ticks_per_quarter_note))
#     cur_track = midi.Track([])
#     cur_track.append(midi.events.SetTempoEvent(tick=0, bpm=b))
#     future_events = {}
#     last_event_tick = 0
#
#     ticks_to_this_tone = 0.0
#     song_events_absolute_ticks = []
#     abs_tick_note_beginning = 0.0
#     for frame in song_data:
#         abs_tick_note_beginning += frame[TICKS_FROM_PREV_START]
#         for subframe in range(tones_per_cell):
#             offset = subframe * NUM_FEATURES_PER_TONE
#             tick_len = int(round(frame[offset + LENGTH]))
#             freq = frame[offset + FREQ]
#             velocity = min(int(round(frame[offset + VELOCITY])), 127)
#             # print('tick_len: {}, freq: {}, velocity: {}, ticks_from_prev_start: {}'.format(tick_len, freq, velocity, frame[TICKS_FROM_PREV_START]))
#             d = freq_to_tone(freq)
#             # print('d: {}'.format(d))
#             if d is not None and velocity > 0 and tick_len > 0:
#                 # range-check with preserved tone, changed one octave:
#                 tone = d['tone']
#                 while tone < 0:   tone += 12
#                 while tone > 127: tone -= 12
#                 pitch_wheel = cents_to_pitchwheel_units(d['cents'])
#                 # print('tick_len: {}, freq: {}, tone: {}, pitch_wheel: {}, velocity: {}'.format(tick_len, freq, tone, pitch_wheel, velocity))
#                 # if pitch_wheel != 0:
#                 # midi.events.PitchWheelEvent(tick=int(ticks_to_this_tone),
#                 #                                            pitch=pitch_wheel)
#                 song_events_absolute_ticks.append((abs_tick_note_beginning,
#                                                    midi.events.NoteOnEvent(
#                                                        tick=0,
#                                                        velocity=velocity,
#                                                        pitch=tone)))
#                 song_events_absolute_ticks.append((abs_tick_note_beginning + tick_len,
#                                                    midi.events.NoteOffEvent(
#                                                        tick=0,
#                                                        velocity=0,
#                                                        pitch=tone)))
#     song_events_absolute_ticks.sort(key=lambda e: e[0])
#     abs_tick_note_beginning = 0.0
#     for abs_tick, event in song_events_absolute_ticks:
#         rel_tick = abs_tick - abs_tick_note_beginning
#         event.tick = int(round(rel_tick))
#         cur_track.append(event)
#         abs_tick_note_beginning = abs_tick
#
#     cur_track.append(midi.EndOfTrackEvent(tick=int(output_ticks_per_quarter_note)))
#     midi_pattern.append(cur_track)
#     # print 'Printing midi track.'
#     # print midi_pattern
#     return midi_pattern


def cents_to_pitchwheel_units(cents):
    return int(40.96 * (float(cents)))


def freq_to_tone(freq):
    """
      returns a dict d where
      d['tone'] is the base tone in midi standard
      d['cents'] is the cents to make the tone into the exact-ish frequency provided.
                 multiply this with 8192 to get the midi pitch level.

      formulas from
        * https://en.wikipedia.org/wiki/MIDI_Tuning_Standard
        * https://en.wikipedia.org/wiki/Cent_(music)
    """
    if freq <= 0.0:
        return None
    float_tone = (69.0 + 12 * math.log(float(freq) / 440.0, 2))
    int_tone = int(float_tone)
    cents = int(1200 * math.log(float(freq) / tone_to_freq(int_tone), 2))
    return {'tone': int_tone, 'cents': cents}


# MUSIC_DIR = "/Users/xwy/Downloads/dataset/MIDIs"
# MUSIC_DIR = "/Users/xwy/Downloads/7"
# MUSIC_DIR = "/Users/xwy/Downloads/piano/midi"
# file_list = []
# song_data = []
# files = os.listdir(MUSIC_DIR)
# i = 0
# for f in files:
#     if (os.path.isfile(MUSIC_DIR + '/' + f)):
#         i = i + 1
#         file_list.append(f)
#         song = read_one_file(MUSIC_DIR, f, False)
#         print song
        # song = np.array(song)
        # print song
        # for k in range(len(song) - 1):
        #     song[k, 0] = song[k+1, 0] - song[k, 0]
        # song[len(song) - 1, 0] = 0
        # song_data.append(song)
        # print(song.shape)
        # print(song)
# pkl.dump(song_data, open("/Users/xwy/Desktop/Study/srtp/midi_out","wb"))


def get_midi_pattern(song_data, b):
    """
    get_midi_pattern takes a song in internal representation
    (a tensor of dimensions [songlength, self.num_song_features]).
    the three values are length, frequency, velocity.
    if velocity of a frame is zero, no midi event will be
    triggered at that frame.

    returns the midi_pattern.

    Can be used with filename == None. Then nothing is saved, but only returned.
    """
    print('song_data[0:10]: {}'.format(song_data[0:10]))

    #
    # Interpreting the midi pattern.
    # A pattern has a list of tracks
    # (midi.Track()).
    # Each track is a list of events:
    #   * midi.events.SetTempoEvent: tick, data([int, int, int])
    #     (The three ints are really three bytes representing one integer.)
    #   * midi.events.TimeSignatureEvent: tick, data([int, int, int, int])
    #     (ignored)
    #   * midi.events.KeySignatureEvent: tick, data([int, int])
    #     (ignored)
    #   * midi.events.MarkerEvent: tick, text, data
    #   * midi.events.PortEvent: tick(int), data
    #   * midi.events.TrackNameEvent: tick(int), text(string), data([ints])
    #   * midi.events.ProgramChangeEvent: tick, channel, data
    #   * midi.events.ControlChangeEvent: tick, channel, data
    #   * midi.events.PitchWheelEvent: tick, data(two bytes, 14 bits)
    #
    #   * midi.events.NoteOnEvent:  tick(int), channel(int), data([int,int]))
    #     - data[0] is the note (0-127)
    #     - data[1] is the velocity.
    #     - if velocity is 0, this is equivalent of a midi.NoteOffEvent
    #   * midi.events.NoteOffEvent: tick(int), channel(int), data([int,int]))
    #
    #   * midi.events.EndOfTrackEvent: tick(int), data()
    #
    # Ticks are relative.
    #
    # Tempo are in microseconds/quarter note.
    #
    # This interpretation was done after reading
    # http://electronicmusic.wikia.com/wiki/Velocity
    # http://faydoc.tripod.com/formats/mid.htm
    # http://www.lastrayofhope.co.uk/2009/12/23/midi-delta-time-ticks-to-seconds/2/
    # and looking at some files. It will hopefully be enough
    # for the use in this project.
    #
    # This approach means that we do not currently support
    #   tempo change events.
    #

    # Tempo:
    # Multiply with output_ticks_pr_input_tick for output ticks.
    midi_pattern = midi.Pattern([], resolution=int(output_ticks_per_quarter_note))
    cur_track = midi.Track([])
    cur_track.append(midi.events.SetTempoEvent(tick=0, bpm=b))
    future_events = {}
    last_event_tick = 0

    ticks_to_this_tone = 0.0
    song_events_absolute_ticks = []
    abs_tick_note_beginning = 0.0
    for frame in song_data:
        abs_tick_note_beginning += frame[TICKS_FROM_PREV_START]
        for subframe in range(tones_per_cell):
            offset = subframe * NUM_FEATURES_PER_TONE
            tick_len = int(round(frame[offset + LENGTH]))
            freq = frame[offset + FREQ]
            velocity = min(int(round(frame[offset + VELOCITY])), 127)
            # print('tick_len: {}, freq: {}, velocity: {}, ticks_from_prev_start: {}'.format(tick_len, freq, velocity, frame[TICKS_FROM_PREV_START]))
            d = freq_to_tone(freq)
            # print('d: {}'.format(d))
            if d is not None and velocity > 0 and tick_len > 0:
                # range-check with preserved tone, changed one octave:
                tone = d['tone']
                while tone < 0:   tone += 12
                while tone > 127: tone -= 12
                pitch_wheel = cents_to_pitchwheel_units(d['cents'])
                # print('tick_len: {}, freq: {}, tone: {}, pitch_wheel: {}, velocity: {}'.format(tick_len, freq, tone, pitch_wheel, velocity))
                # if pitch_wheel != 0:
                # midi.events.PitchWheelEvent(tick=int(ticks_to_this_tone),
                #                                            pitch=pitch_wheel)
                song_events_absolute_ticks.append((abs_tick_note_beginning,
                                                   midi.events.NoteOnEvent(
                                                       tick=0,
                                                       velocity=velocity,
                                                       pitch=tone)))
                song_events_absolute_ticks.append((abs_tick_note_beginning + tick_len,
                                                   midi.events.NoteOffEvent(
                                                       tick=0,
                                                       velocity=0,
                                                       pitch=tone)))
    song_events_absolute_ticks.sort(key=lambda e: e[0])
    abs_tick_note_beginning = 0.0
    for abs_tick, event in song_events_absolute_ticks:
        rel_tick = abs_tick - abs_tick_note_beginning
        event.tick = int(round(rel_tick))
        cur_track.append(event)
        abs_tick_note_beginning = abs_tick

    cur_track.append(midi.EndOfTrackEvent(tick=int(output_ticks_per_quarter_note)))
    midi_pattern.append(cur_track)
    # print 'Printing midi track.'
    # print midi_pattern
    return midi_pattern


def save_midi_pattern(filename, midi_pattern):
    if filename is not None:
        try:
            midi.write_midifile(filename, midi_pattern)
        except PermissionError:
            return False
        else:
            return True
    return False


def save_data(filename, song_data, b):
    """
    save_data takes a filename and a song in internal representation
    (a tensor of dimensions [songlength, 3]).
    the three values are length, frequency, velocity.
    if velocity of a frame is zero, no midi event will be
    triggered at that frame.

    returns the midi_pattern.

    Can be used with filename == None. Then nothing is saved, but only returned.
    """
    midi_pattern = get_midi_pattern(song_data, b)
    res = save_midi_pattern(filename, midi_pattern)
    return res
