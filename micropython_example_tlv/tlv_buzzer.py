import struct

from micropython import const
from time import sleep_ms
from machine import Pin, PWM

import tlv_types

_NOTE_FMT = '!fHH'
_NOTE_FMT_CALCSIZE = struct.calcsize(_NOTE_FMT)

buzzer_pin = Pin(32, Pin.OUT)


def note(sw_freq: int, sw_duration: int, sw_sleep: int, active_duty: int = 50, buz: PWM | None = None):
    if buz is None:
        my_buz = PWM(buzzer_pin)
    else:
        my_buz = buz
    my_buz.freq(int(sw_freq))
    my_buz.duty(active_duty)
    sleep_ms(sw_duration)
    my_buz.duty(0)
    sleep_ms(sw_sleep)

    if buz is None:
        my_buz.deinit()


def play(sw_notes, sw_duration, sw_sleep, active_duty=50):
    buz = PWM(buzzer_pin)
    for i, freq in enumerate(sw_notes):
        note(freq, sw_duration[i], sw_sleep[i], active_duty, buz)
    buz.duty(0)
    buz.deinit()


rd2d = const(1)
star_wars = const(2)
reload = const(3)
ringtone = const(4)


def buzzer_r2d2():
    r2_d2_notes = [3520, 3135.96, 2637.02, 2093, 2349.32, 3951.07, 2793.83, 4186.01, 3520, 3135.96, 2637.02, 2093,
                   2349.32, 3951.07, 2793.83, 4186.01]
    r2_d2_duration = [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80]
    r2_d2_sleep = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    play(r2_d2_notes, r2_d2_duration, r2_d2_sleep)


def buzzer_star_wars():
    sw_notes = [293.66, 293.66, 293.66, 392.0, 622.25, 554.37, 523.25, 454, 932.32, 622.25, 554.37, 523.25, 454, 932.32,
                622.25, 554.37, 523.25, 554.37, 454]
    sw_duration = [180, 180, 180, 800, 800, 180, 180, 180, 800, 400, 180, 180, 180, 800, 400, 180, 180, 180, 1000]
    sw_sleep = [40, 40, 40, 100, 100, 40, 40, 40, 100, 50, 40, 40, 40, 100, 50, 40, 40, 40, 100]
    play(sw_notes, sw_duration, sw_sleep)


def buzzer_reload():
    sw_notes = list(range(400, 1400, 20))
    sw_duration = list(range(120, 20, -2))
    sw_sleep = [20] * 50
    play(sw_notes, sw_duration, sw_sleep)


def buzzer_ringtone():
    sw_notes = [659.25, 587.33, 369.99, 415.3, 554.37, 493.88, 293.66, 329.63, 493.88, 440, 277.18, 329.63, 440]
    sw_duration = [120, 120, 240, 240, 120, 120, 240, 240, 120, 120, 240, 240, 720]
    sw_sleep = [20] * 50
    play(sw_notes, sw_duration, sw_sleep)


def note_to_bytes(sw_freq: float, sw_duration: int, sw_sleep: int) -> bytes:
    return struct.pack(_NOTE_FMT, sw_freq, sw_duration, sw_sleep)


def apply_note(tlv_data: bytes) -> None:
    sw_freq, sw_duration, sw_sleep = struct.unpack(_NOTE_FMT, tlv_data)
    note(sw_freq, sw_duration, sw_sleep, buz=None)


def song_to_bytes(song) -> bytes:
    return struct.pack('<B', song)


def apply_song(tlv_data: bytes) -> None:
    song = struct.unpack("<B", tlv_data)[0]
    if song == rd2d:
        buzzer_r2d2()
    elif song == star_wars:
        buzzer_star_wars()
    elif song == reload:
        buzzer_reload()
    elif song == ringtone:
        buzzer_ringtone()
    else:
        print(f"unknown song id: {song}")


def append_mappings(tlv_parser) -> None:
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_buzzer_note, _NOTE_FMT_CALCSIZE, apply_note)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_buzzer_song, 1, apply_song)
