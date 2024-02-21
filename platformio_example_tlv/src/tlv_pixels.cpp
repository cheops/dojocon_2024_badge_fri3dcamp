#include "tlv_pixels.h"
#include <Adafruit_NeoPixel.h>

static const uint16_t LED_COUNT = 5;
static const uint16_t LED_PIN = 2;
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);


void apply_pixels_clear(const uint8_t* tlv_value) {
    strip.clear();
    strip.show();
}


void apply_pixels_set_color(const uint8_t* tlv_value) {
    strip.fill(strip.Color(tlv_value[0], tlv_value[1], tlv_value[2]));
    strip.show();
}


void apply_pixels_set_i_color(const uint8_t* tlv_value) {
    strip.setPixelColor(tlv_value[0], strip.Color(tlv_value[1], tlv_value[2], tlv_value[3]));
    strip.show();
}


void apply_pixels_set_5_color(const uint8_t* tlv_value) {
    for (size_t i = 0; i < LED_COUNT; i++)
    {
      strip.setPixelColor(i, strip.Color(tlv_value[3*i], tlv_value[3*i+1], tlv_value[3*i+2]));
    }
    strip.show();
}
