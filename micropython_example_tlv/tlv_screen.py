import struct

from machine import Pin, SPI
# from machine import SoftI2C
# from lis2hh12_dev import LIS2HH12, SF_G
import gc
import st7789

import chango_16 as font_16

import tlv_types

SCREEN_COLOR_FMT = '!H'

setup_ready = False


def _screen_setup():
    spi = SPI(2, baudrate=40000000, polarity=1)
    pcs = Pin(5, Pin.OUT)
    pdc = Pin(33, Pin.OUT)

    gc.collect()  # Precaution before instantiating framebuffer

    screen = st7789.ST7789(
        spi=spi,
        width=240,
        height=240,
        cs=pcs,
        dc=pdc,
        buffer_size=240 * 240 * 2)
    screen.init()

    return screen


# def _turn_on_backlight():
#     i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
#     imu = LIS2HH12(i2c, address=0x18, sf=SF_G)
#     # enable the ACC interrupt to turn on backlight
#     imu.enable_act_int()


if not setup_ready:
    # _turn_on_backlight()

    # can be used as globals
    # import hardware
    # hardware.tft
    tft = _screen_setup()

    setup_ready = True

"""
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF
"""
screen_colors = st7789.BLACK, st7789.BLUE, st7789.RED, st7789.GREEN, st7789.CYAN, st7789.MAGENTA, st7789.YELLOW, st7789.WHITE


def screen_color_to_bytes(color: int) -> bytes:
    return struct.pack(SCREEN_COLOR_FMT, color)


def apply_screen_clear(tlv_value: bytes) -> None:
    tft.fill(st7789.BLACK)


def apply_screen_color(tlv_value: bytes) -> None:
    color = struct.unpack(SCREEN_COLOR_FMT, tlv_value)[0]
    tft.fill(color)


offset = 0
font_size = 16


def apply_screen_text(tlv_value: bytes) -> None:
    global offset
    dynamic_format = '<' + str(len(tlv_value)) + 's'
    text = struct.unpack(dynamic_format, tlv_value)[0]

    if offset >= tft.height():
        offset = 0
    if offset == 0:
        tft.fill(st7789.BLACK)

    tft.write(font_16, text, 0, offset)
    offset += font_size


def append_mappings(tlv_parser) -> None:
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_screen_clear, 0, apply_screen_clear)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_screen_color, 2, apply_screen_color)
    tlv_parser.add_tlv_mapping(tlv_types.tlv_type_screen_text, None, apply_screen_text)
