import simpleaudio as sa


def _play_sound(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing


def correct_sound():
    _play_sound("assets/correct.wav")


def incorrect_sound():
    _play_sound("assets/wrong.wav")
