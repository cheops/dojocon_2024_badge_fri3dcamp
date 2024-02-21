from micropython_example_tlv.tlv import TLVParser

import struct

RGB_COLOR_FMT = '<BBB'

test_tlv_1 = b'\x01\x03\x64\x64\x64'
test_tlv_2 = b'\x02\x04\x01\x64\x64\x64'


def set_color(r, g, b):
    pass


example_0 = "0x00 0x00"
example_1 = "0x01 0x03 0x64 0x64 0x64"
example_2 = "0x02 0x04 0x00 0x64 0x64 0x64"
example_3 = "0x03 0x0e 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64"

tlv_type_pixels_clear = 0
tlv_type_pixels_set_color = 1
tlv_type_pixels_set_i_color = 2
tlv_type_pixels_set_5_color = 3


def apply_pixels_set_color(tlv_value: bytes):
    color = bytes_to_rgb(tlv_value)
    print(f"pixels_set_color {color=}")


def apply_pixels_set_i_color(tlv_value: bytes):
    i = struct.unpack_from('<B', tlv_value, 0)[0]
    color = bytes_to_rgb(tlv_value, 1)
    print(f"pixels_set_i_color {i=} {color=}")


def apply_pixels_set_5_color(tlv_value: bytes):
    colors = []
    for i in range(5):
        color_i = bytes_to_rgb(tlv_value, i * struct.calcsize(RGB_COLOR_FMT))
        colors.append(color_i)
    print(f"pixels_set_5_color {colors=}")


def rgb_to_bytes(r: int, g: int, b: int) -> bytes:
    return struct.pack(RGB_COLOR_FMT, r, g, b)


def bytes_to_rgb(b: bytes, offset: int = 0) -> (int, int, int):
    return struct.unpack_from(RGB_COLOR_FMT, b, offset)


def color_rainbow():
    metallic_violet = (70, 1, 155)
    azure = (0, 126, 254)
    islamic_green = (0, 187, 0)
    cadmium_yellow = (254, 246, 1)
    electric_red = (221, 0, 0)
    return (rgb_to_bytes(*metallic_violet) +
            rgb_to_bytes(*azure) +
            rgb_to_bytes(*islamic_green) +
            rgb_to_bytes(*cadmium_yellow) +
            rgb_to_bytes(*electric_red)
            )


def main():
    print("running main")

    tlv_parser = TLVParser()

    tlv_parser.add_tlv_mapping(tlv_type_pixels_set_color, 3, apply_pixels_set_color)
    tlv_parser.add_tlv_mapping(tlv_type_pixels_set_i_color, 4, apply_pixels_set_i_color)
    tlv_parser.add_tlv_mapping(tlv_type_pixels_set_5_color, 15, apply_pixels_set_5_color)

    decoded = tlv_parser.decode(test_tlv_1)
    print(f"{len(decoded)=} {decoded=}")
    tlv_parser.apply_tlvs(decoded)

    decoded = tlv_parser.decode(test_tlv_1 + test_tlv_2)
    print(f"{len(decoded)=} {decoded=}")
    tlv_parser.apply_tlvs(decoded)

    # now encode en decode and apply

    encoded = tlv_parser.encode(tlv_type_pixels_set_color, b'\x64\x64\x64')
    print(f"{len(encoded)=} {encoded=} {encoded.hex()=}")
    decoded = tlv_parser.decode(encoded)
    tlv_parser.apply_tlvs(decoded)

    encoded = tlv_parser.encode(tlv_type_pixels_set_i_color, struct.pack('<B', 1) + rgb_to_bytes(100, 200, 255))
    print(f"{len(encoded)=} {encoded=} {encoded.hex()=}")
    decoded = tlv_parser.decode(encoded)
    tlv_parser.apply_tlvs(decoded)

    combined_encoded = b''
    color = 5 * b'\x64\x64\x64'
    combined_encoded += tlv_parser.encode(tlv_type_pixels_set_5_color, color)
    print(f"{len(combined_encoded)=} {combined_encoded=} {combined_encoded.hex()=}")
    decoded = tlv_parser.decode(encoded)
    tlv_parser.apply_tlvs(decoded)

    encoded = tlv_parser.encode(tlv_type_pixels_set_5_color, color_rainbow())
    print(f"{len(encoded)=} {encoded=} {encoded.hex()=}")
    decoded = tlv_parser.decode(encoded)
    tlv_parser.apply_tlvs(decoded)

    encoded = tlv_parser.encode(10, b'')
    print(f"{len(encoded)=} {encoded=} {encoded.hex()=}")
    decoded = tlv_parser.decode(encoded)
    tlv_parser.apply_tlvs(decoded)

    p = struct.pack('<B', 1)
    print(f"{len(p)=} {p=} {p.hex()=}")

    tlv_type, tlv_length = struct.unpack('<BB', test_tlv_1[:2])
    print(f"{tlv_type=} {tlv_length=}")

    n = struct.pack('<5s', b'ex3_b')
    print(f"{n=} {n.hex()=}")
    s = bytes().fromhex('6578335f62')
    print(f"{s=}")

    n = struct.pack('<BB', 2, 1)
    print(f"{n=} {n.hex()=}")
    s = bytes().fromhex('6578335f62')
    print(f"{s=}")

    t = struct.unpack('<H', b'\xff\xff')[0]
    print(t)


if __name__ == "__main__":
    print("need to run main")
    main()
