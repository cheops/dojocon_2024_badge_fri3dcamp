#ifndef tlv_screen_h
#define tlv_screen_h

#include "tlv_types.h"

void apply_screen_clear(const uint8_t* tlv_value);
void apply_screen_color(const uint8_t* tlv_value);
void apply_screen_text(const uint8_t* tlv_value, const uint8_t tlv_length);

#endif // tlv_screen_h
