from micropython import const
import struct

import pixels
import tlv_types

_RGB_COLOR_FMT = const('!BBB')
_RGB_COLOR_FMT_CALCSIZE = struct.calcsize(_RGB_COLOR_FMT)


def apply_pixels_clear(tlv_value: bytes):
    pixels.clear()


def apply_pixels_set_color(tlv_value: bytes):
    color = bytes_to_rgb(tlv_value)
    pixels.set_color(*color)


def apply_pixels_set_i_color(tlv_value: bytes):
    i = struct.unpack_from('<B', tlv_value, 0)[0]
    color = bytes_to_rgb(tlv_value, 1)
    pixels.set_i_color(i, *color)


def apply_pixels_set_5_color(tlv_value: bytes):
    for i in range(5):
        color_i = bytes_to_rgb(tlv_value, i * _RGB_COLOR_FMT_CALCSIZE)
        pixels.set_i_color(i, *color_i)


def rgb_to_bytes(r: int, g: int, b: int) -> bytes:
    return struct.pack(_RGB_COLOR_FMT, r, g, b)


def bytes_to_rgb(b: bytes, offset: int = 0) -> (int, int, int):
    return struct.unpack_from(_RGB_COLOR_FMT, b, offset)


def rgb_n_to_bytes(colors: list[int, int, int]) -> bytes:
    b = bytes()
    for i in range(len(colors)):
        b += rgb_to_bytes(*colors[i])
    return b


def color_rainbow():
    metallic_violet = (70, 1, 155)
    azure = (0, 126, 254)
    islamic_green = (0, 187, 0)
    cadmium_yellow = (254, 246, 1)
    electric_red = (221, 0, 0)
    return (metallic_violet,
            azure,
            islamic_green,
            cadmium_yellow,
            electric_red
            )


def rainbow_generator() -> list[int, int, int]:
    colors = color_rainbow()
    for i in range(pixels.NUM_LEDS):
        cs = []
        for j in range(len(colors)):
            index = j - i
            while index < 0:
                index += len(colors)
            cs.append(colors[index])
        yield cs


def append_mappings(tlv_parser) -> None:
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_pixels_clear, 0, apply_pixels_clear)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_pixels_set_color, _RGB_COLOR_FMT_CALCSIZE, apply_pixels_set_color)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_pixels_set_i_color, 1 + _RGB_COLOR_FMT_CALCSIZE,
                               apply_pixels_set_i_color)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_pixels_set_5_color, 5 * _RGB_COLOR_FMT_CALCSIZE,
                               apply_pixels_set_5_color)
