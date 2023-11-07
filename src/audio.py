# simpleaudio is not available with Pydroid 3 on mobile - thus the try-except-statements.

try:
    import simpleaudio as sa
except:
    pass


def _play_sound(filename):
    try:
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
    except:
        pass


def correct_sound():
    _play_sound("assets/correct.wav")


def incorrect_sound():
    _play_sound("assets/wrong.wav")
