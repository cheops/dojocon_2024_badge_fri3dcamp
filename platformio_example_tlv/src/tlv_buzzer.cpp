#include <Arduino.h>
#include "tlv_buzzer.h"
#include <Badge2020_Buzzer.h>
#include <arpa/inet.h>

Badge2020_Buzzer buzzer;

// function definitions
void buzzer_reload(const uint16_t &duration_ms);
void buzzer_ringtone();

float ReverseFloat(const uint8_t *floatToConvert)
{
    // ntohl does not seem to work on ESP32
    float retVal;
    char *returnFloat = (char *)&retVal;

    // swap the bytes into a temporary buffer
    returnFloat[0] = floatToConvert[3];
    returnFloat[1] = floatToConvert[2];
    returnFloat[2] = floatToConvert[1];
    returnFloat[3] = floatToConvert[0];

    return retVal;
}

void apply_buzzer_note(const uint8_t *tlv_value)
{
    float frequency = ReverseFloat(tlv_value);

    uint16_t duration;
    memcpy(&duration, tlv_value + 4, sizeof(duration));
    duration = ntohs(duration);

    uint16_t sleep;
    memcpy(&sleep, tlv_value + 4 + 2, sizeof(sleep));
    sleep = ntohs(sleep);

    buzzer.setVolume(255);
    buzzer.setFrequency(frequency);
    delay(duration);
    buzzer.setVolume(0);
    delay(sleep);
}

void apply_buzzer_song(const uint8_t *tlv_value)
{
    switch (tlv_value[0])
    {
    case buzzer_song_reload:
        buzzer_reload(4550);
        break;

    case buzzer_song_ringtone:
        buzzer_ringtone();
        break;

    default:
        log_d("not implemented song %u", tlv_value[0]);
        break;
    }
}

void buzzer_reload(const uint16_t &duration_ms)
{
    log_d(":: buzzer reload - duration_ms=%u", duration_ms);
    const uint16_t buzzer_start_freq = 400;
    const uint16_t buzzer_end_freq = 1400;
    const uint8_t total_reload_time_steps = 100;
    const int64_t reload_time_interval_us = duration_ms * 1000 / total_reload_time_steps;

    buzzer.setVolume(255);
    bool reloading = true;

    int64_t start_time = esp_timer_get_time();
    int64_t last_reload_time = start_time;

    while (reloading)
    {
        int64_t current_time = esp_timer_get_time();
        if (current_time - last_reload_time > reload_time_interval_us)
        {
            uint8_t percent = uint8_t((current_time - start_time) / reload_time_interval_us);
            if (percent >= 100)
            {
                percent = 100;
                reloading = false;
            }

            buzzer.setFrequency(buzzer_start_freq + (percent * (buzzer_end_freq - buzzer_start_freq) / total_reload_time_steps));
            last_reload_time = esp_timer_get_time();
            ;
        }
        vTaskDelay(reload_time_interval_us / 1000 / 2 / portTICK_PERIOD_MS);
    }
    buzzer.setVolume(0);
}

void buzzer_ringtone()
{
    float notes[13] = {659.25, 587.33, 369.99, 415.3, 554.37, 493.88, 293.66, 329.63, 493.88, 440, 277.18, 329.63, 440};
    float lengths[13] = {1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 6};

    buzzer.setVolume(255);

    for (int i = 0; i < 13; i++)
    {
        buzzer.setFrequency(notes[i]);
        delay(120 * lengths[i]);
    }

    buzzer.setVolume(0);
}
