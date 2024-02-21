# Helpers for generating BLE advertising payloads.

from micropython import const
import struct
import bluetooth

# Advertising payloads are repeated packets of the following form:
#   1 byte data length (N + 1)
#   1 byte type (see constants below)
#   N bytes type-specific data

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)
_ADV_TYPE_MANUFACTURER_SPECIFIC_DATA = const(0xff)


# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(limited_disc=None, br_edr=None, name=None, services=None, appearance=None, company_id=None, man_spec_data=None):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack('BB', len(value) + 1, adv_type) + value

    if limited_disc is not None or br_edr is not None:
        _append(_ADV_TYPE_FLAGS, struct.pack('B', (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    if company_id and man_spec_data:
        # company_id should be 2 bytes long
        # man_spec_data also in bytes
        data = company_id + man_spec_data
        _append(_ADV_TYPE_MANUFACTURER_SPECIFIC_DATA, data)

    if appearance:
        # See org.bluetooth.characteristic.gap.appearance.xml
        _append(_ADV_TYPE_APPEARANCE, struct.pack('<h', appearance))

    if len(payload) > 31:
        raise RuntimeError("max advertising payload 31, got: " + str(len(payload)))
    return payload


def decode_field(payload, adv_type):
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2:i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def decode_name(payload):
    n = decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], 'utf-8') if n else ''


def decode_services(payload):
    services = []
    for u in decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack('<h', u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack('<d', u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(bluetooth.UUID(u))
    return services


def decode_man_spec_data(payload):
    n = decode_field(payload, _ADV_TYPE_MANUFACTURER_SPECIFIC_DATA)
    if len(n) > 0 and len(n[0]) > 2:
        return n[0][:2], n[0][2:]  # company_id, manufacturer_specific_data
    else:
        return b'', b''


def demo():
    payload = advertising_payload(name='micropython', services=[bluetooth.UUID(0x181A), bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')])
    print(payload)
    print(decode_name(payload))
    print(decode_services(payload))

    payload_2 = advertising_payload(company_id=b'\xff\xff', man_spec_data=b'\xde\xad\xbe\xef\xca\xfe')
    print(payload_2)
    print(decode_man_spec_data(payload_2))


if __name__ == '__main__':
    demo()
