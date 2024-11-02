import argparse
import pretty_midi
import librosa.display
import matplotlib.pyplot as plt
import os
import subprocess

__all__ = ['FluidSynth']

DEFAULT_SOUND_FONT = '~/.fluidsynth/default_sound_font.sf2'
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_GAIN = 0.2

class FluidSynth():
    def __init__(self, sound_font=DEFAULT_SOUND_FONT, sample_rate=DEFAULT_SAMPLE_RATE, gain=DEFAULT_GAIN):
        self.sample_rate = sample_rate
        self.sound_font = os.path.expanduser(sound_font)
        self.gain = gain

    def midi_to_audio(self, midi_file: str, audio_file: str, verbose=True):
        if verbose:
            stdout = None
        else:
            stdout = subprocess.DEVNULL
        subprocess.call(
            ['fluidsynth', '-ni', '-g', str(self.gain), self.sound_font, midi_file, '-F', audio_file, '-r', str(self.sample_rate)],
            stdout=stdout,
        )

    def play_midi(self, midi_file):
        subprocess.call(['fluidsynth', '-i', '-g', str(self.gain), self.sound_font, midi_file, '-r', str(self.sample_rate)])
        
        
        
def show_midi_info(midi_path, print_notes=False):
  midi_data = pretty_midi.PrettyMIDI(midi_path)
  print("Instruments: ", [instrument.name for instrument in midi_data.instruments])
  print("MIDI duration: {duration:.2f} seconds".format(duration=midi_data.get_end_time()))
  if print_notes:
    for instrument in midi_data.instruments:
      print(instrument.name)
      for note in instrument.notes:
        print(note.start, note.end, note.pitch, note.velocity)

def piano_roll(midi_path):
  plt.figure(figsize=(12, 4))
  plot_piano_roll(midi_path, 24, 84)

def plot_piano_roll(path, start_pitch, end_pitch, fs=100):
    midi_data = pretty_midi.PrettyMIDI(path)
    # Use librosa's specshow function for displaying the piano roll
    librosa.display.specshow(midi_data.get_piano_roll(fs)[start_pitch:end_pitch],
                             hop_length=1, sr=fs, x_axis='time', y_axis='cqt_note',
                             fmin=pretty_midi.note_number_to_hz(start_pitch))

def change_midi_velocity(midi_path, output_path, delta=0): # Renamed the function to avoid name conflict
  midi_data = pretty_midi.PrettyMIDI(midi_path)
  for instrument in midi_data.instruments:
    for note in instrument.notes:
      note.velocity += delta
  midi_data.write(output_path)

def convert_midi_to_wav(soundfont_path, midi_path, output_path, gain=None, velocity_change=0): # Renamed the argument
  change_midi_velocity(midi_path, "temp.mid", delta=velocity_change) # Call the renamed function
  FluidSynth(soundfont_path, gain=gain).midi_to_audio("temp.mid", output_path)
  os.remove("temp.mid")


def trim_midi(midi_path, start, end):
  import mido
  import midi_clip
  mid = mido.MidiFile(midi_path)
  trimmed_midi = midi_clip.midi_clip(mid, start, end)

  dir_name, base_name = os.path.split(midi_path)
  new_base_name = "trimmed_" + base_name
  output_path = os.path.join(dir_name, new_base_name)
  trimmed_midi.save(output_path)
  return output_path

def playMidi(midi_file_path,
             soundfont_path="/content/guGS.sf2",
             output_path="audio.wav",
             start=None,
             end=None,
             gain=DEFAULT_GAIN,
             velocity_change=0
             ):
    from IPython.display import Audio

    if start is not None and end is not None:
      midi_file_path = trim_midi(midi_file_path, start, end)
      convert_midi_to_wav(soundfont_path, midi_file_path, output_path, gain=gain, velocity_change=velocity_change)
      os.remove(midi_file_path)
    else:
      convert_midi_to_wav(soundfont_path, midi_file_path, output_path, gain=gain, velocity_change=velocity_change)
    return Audio(output_path)