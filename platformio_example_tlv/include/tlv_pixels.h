#ifndef tlv_pixels_h
#define tlv_pixels_h

#include "tlv_types.h"

void apply_pixels_clear(const uint8_t* tlv_value);
void apply_pixels_set_color(const uint8_t* tlv_value);
void apply_pixels_set_i_color(const uint8_t* tlv_value);
void apply_pixels_set_5_color(const uint8_t* tlv_value);

#endif // tlv_pixels_h
