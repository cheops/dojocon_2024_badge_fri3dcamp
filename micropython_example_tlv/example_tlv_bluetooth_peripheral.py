import bluetooth
import time
from ble_advertising import advertising_payload
from tlv import TLVParser
import tlv_pixels
import tlv_screen
import tlv_buzzer

from micropython import const

_OUR_COMPANY_ID = const(b'\xff\xff')

tlv_parser = TLVParser()

tlv_pixels.append_mappings(tlv_parser)
tlv_screen.append_mappings(tlv_parser)
tlv_buzzer.append_mappings(tlv_parser)


class BLESimplePeripheral:
    def __init__(self, name: str | None = "ble_peripheral"):
        self._ble = bluetooth.BLE()
        self._name = name
        self._payload = bytearray()

    def __enter__(self):
        print("activate ble")
        self._ble.active(True)
        # give ble some time to activate
        time.sleep_ms(200)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(f"{exc_type=} {exc_value=} {exc_tb=}")
        print("deactivate ble")
        self._ble.active(False)
        # give ble some time to deactivate
        time.sleep_ms(400)

    def man_spec_data(self, man_spec_data: bytes = b'') -> None:
        self._payload = advertising_payload(name=self._name, company_id=_OUR_COMPANY_ID, man_spec_data=man_spec_data)

    def start_advertise(self, interval_us: int = 40_000) -> None:
        # print("start advertise")
        self._ble.gap_advertise(interval_us, adv_data=self._payload, connectable=False)

    def stop_advertise(self) -> None:
        # print("stop advertise")
        self._ble.gap_advertise(None)


def apply_and_broadcast(per: BLESimplePeripheral, encoded: bytes, delay_ms: int = 200) -> None:
    decoded = tlv_parser.decode(encoded)

    per.man_spec_data(encoded)
    per.start_advertise(40_000)

    tlv_parser.apply_tlvs(decoded)
    
    time.sleep_ms(delay_ms)
    per.stop_advertise()


def pixels_clear(per: BLESimplePeripheral, delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_pixels.tlv_types.tlv_type_pixels_clear, b'')
    apply_and_broadcast(per, encoded, delay_ms)


def pixels_set_5_colors(per: BLESimplePeripheral, colors: list[int, int, int], delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_pixels.tlv_types.tlv_type_pixels_set_5_color, tlv_pixels.rgb_n_to_bytes(colors))
    apply_and_broadcast(per, encoded, delay_ms)


def rainbow(per: BLESimplePeripheral, delay_ms: int = 200) -> None:
    try:
        for _ in range(1):
            for colors in tlv_pixels.rainbow_generator():
                pixels_set_5_colors(per, colors, delay_ms)
    except KeyboardInterrupt:
        pass
    finally:
        pixels_clear(per)


def screen_clear(per: BLESimplePeripheral, delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_screen.tlv_types.tlv_type_screen_clear, b'')
    apply_and_broadcast(per, encoded, delay_ms)


def screen_color(per: BLESimplePeripheral, color: int, delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_screen.tlv_types.tlv_type_screen_color, tlv_screen.screen_color_to_bytes(color))
    apply_and_broadcast(per, encoded, delay_ms)


def screen_color_cycler(per: BLESimplePeripheral, delay_ms: int = 200) -> None:
    try:
        for _ in range(1):
            for color in tlv_screen.screen_colors:
                screen_color(per, color, delay_ms)
    except KeyboardInterrupt:
        pass
    finally:
        screen_clear(per)


def screen_text(per: BLESimplePeripheral, text: bytes, delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_screen.tlv_types.tlv_type_screen_text, text)
    apply_and_broadcast(per, encoded, delay_ms)


def buzzer_note(per: BLESimplePeripheral, sw_freq: int, sw_duration: int, sw_sleep: int, delay_ms: int = 200) -> None:
    encoded = tlv_parser.encode(tlv_buzzer.tlv_types.tlv_type_buzzer_note,
                                tlv_buzzer.note_to_bytes(sw_freq, sw_duration, sw_sleep))
    apply_and_broadcast(per, encoded, delay_ms)


def buzzer_song(per: BLESimplePeripheral, song: int, delay_ms: int = 200) -> None:
    
    encoded = tlv_parser.encode(tlv_buzzer.tlv_types.tlv_type_buzzer_song, tlv_buzzer.song_to_bytes(song))
    apply_and_broadcast(per, encoded, delay_ms)


def peripheral():
    with BLESimplePeripheral(name=None) as per:
        while True:
            # buzzer_song(per, tlv_buzzer.rd2d, 500)
            # buzzer_song(per, tlv_buzzer.star_wars, 500)
            buzzer_song(per, tlv_buzzer.reload, 2_000)
            buzzer_song(per, tlv_buzzer.ringtone, 2_000)

            buzzer_note(per, 400, 100, 20, 500)
            buzzer_note(per, 450, 100, 20, 500)
            buzzer_note(per, 500, 100, 20, 500)
            buzzer_note(per, 400, 100, 20, 500)
            buzzer_note(per, 500, 100, 20, 500)
            buzzer_note(per, 550, 100, 20, 500)
            buzzer_note(per, 600, 100, 20, 500)

            rainbow(per, 500)
            pixels_clear(per, 500)
            
            screen_color_cycler(per, 500)
            screen_clear(per, 500)
            
            screen_color(per, tlv_screen.st7789.RED, 1_000)
            
            for _ in range(10):
                screen_text(per, b'Hello Joram', 500)
                screen_text(per, b'Hello Jan', 500)
                screen_text(per, b'Hello Bart', 500)
            
            screen_color(per, tlv_screen.st7789.BLUE, 1_000)
            
            screen_clear(per)


def main():
    print("running main")

    peripheral()


if __name__ == "__main__":
    print("we need to run main")
    main()
