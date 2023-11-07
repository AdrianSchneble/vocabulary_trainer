import io

import pygame
from gtts import gTTS

pygame.mixer.init()


def _play_sound(filename) -> None:
    # pygame doesn't work on mobile, hence the try-except
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except:
        pass


def correct_sound() -> None:
    _play_sound("assets/correct.wav")


def incorrect_sound() -> None:
    _play_sound("assets/wrong.wav")


def play_vocabulary_tts(vocabulary: str) -> None:
    # pygame doesn't work on mobile, hence the try-excepts. Also, gtts requires internet.
    try:
        tts = gTTS(vocabulary, lang="ko")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()
    except:
        pass
