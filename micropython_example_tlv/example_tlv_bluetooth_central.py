import bluetooth
import time
from ble_advertising import decode_man_spec_data, decode_name
from tlv import TLVParser
import tlv_pixels
import tlv_screen
import tlv_buzzer

from micropython import const

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)
_ADV_SCAN_RSP = const(0x04)

_OUR_COMPANY_ID = const(b'\xff\xff')

tlv_parser = TLVParser()

tlv_pixels.append_mappings(tlv_parser)
tlv_screen.append_mappings(tlv_parser)
tlv_buzzer.append_mappings(tlv_parser)


class BLESimpleCentral:
    def __init__(self, wanted_name: str | None, min_rssi: int = None):
        self._wanted_name = wanted_name
        self._min_rssi = min_rssi

        self._ble = bluetooth.BLE()
        self._scan_result_callback = None
        self._stop_scanning = False

    def __enter__(self):
        print("activate ble")
        self._ble.active(True)
        self._ble.irq(self._irq)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(f"{exc_type=} {exc_value=} {exc_tb=}")
        print("deactivate ble")
        self._ble.active(False)

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            # print("addr_type=", addr_type, ", addr=", bytes(addr), ", adv_type=", adv_type, ", rssi=", rssi, "adv_data=", bytes(adv_data))
            # print("name: ", decode_name(bytes(adv_data)))
            if ((self._min_rssi is not None and rssi > self._min_rssi)
                    or self._min_rssi is None):
                if adv_type == _ADV_SCAN_IND:

                    if ((self._wanted_name is not None and self._wanted_name == decode_name(adv_data))
                            or self._wanted_name is None):

                        c_id, man_spec_data = decode_man_spec_data(adv_data)
                        if _OUR_COMPANY_ID == c_id:
                            # Found the required broadcast message, call our callback
                            if self._scan_result_callback:
                                self._scan_result_callback(bytes(man_spec_data))

        elif event == _IRQ_SCAN_DONE:
            # scanning finished, restart it if needed
            if not self._stop_scanning:
                self._ble.gap_scan(2_000, 120_000, 100_000, False)  # scan during 2 seconds, every 120ms for 100ms

    def scan(self, callback=None):
        print("start listening for broadcast messages")
        self._scan_result_callback = callback
        self._ble.gap_scan(2_000, 120_000, 100_000, False)  # scan during 2 seconds, every 120ms for 100ms

    def stop_scanning(self):
        print("stop scanning as fast as we can")
        self._stop_scanning = True
        self._scan_result_callback = None
        self._ble.gap_scan(None)


def central():
    with BLESimpleCentral(wanted_name=None, min_rssi=-70) as cen:
        last_data = b''

        def on_scan_result(data):
            nonlocal last_data
            if data != last_data:
                last_data = data
                decoded = tlv_parser.decode(data)
                tlv_parser.apply_tlvs(decoded)

        try:
            cen.scan(callback=on_scan_result)
            while True:
                time.sleep_ms(10)
        except KeyboardInterrupt:
            cen.stop_scanning()
        finally:
            tlv_pixels.pixels.clear()
            tlv_screen.tft.fill(tlv_screen.st7789.BLACK)


def main():
    print("running main")

    central()


if __name__ == "__main__":
    print("we need to run main")
    main()
