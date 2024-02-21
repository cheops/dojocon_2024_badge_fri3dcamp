#ifndef tlv_buzzer_h
#define tlv_buzzer_h

#include "tlv_types.h"

const uint8_t buzzer_song_rd2d = 1;
const uint8_t buzzer_song_star_wars = 2;
const uint8_t buzzer_song_reload = 3;
const uint8_t buzzer_song_ringtone = 4;

void apply_buzzer_note(const uint8_t* tlv_value);
void apply_buzzer_song(const uint8_t* tlv_value);

#endif // tlv_buzzer_h
