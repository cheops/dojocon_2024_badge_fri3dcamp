#ifndef tlv_types_h
#define tlv_types_h

#include <stdint.h>

const uint8_t tlv_type_pixels_clear = 0;
const uint8_t tlv_type_pixels_set_color = 1;
const uint8_t tlv_type_pixels_set_i_color = 2;
const uint8_t tlv_type_pixels_set_5_color = 3;

const uint8_t tlv_type_screen_clear = 10;
const uint8_t tlv_type_screen_color = 11;
const uint8_t tlv_type_screen_text = 12;

const uint8_t tlv_type_buzzer_note = 20;
const uint8_t tlv_type_buzzer_song = 21;

#endif // tlv_types_h
