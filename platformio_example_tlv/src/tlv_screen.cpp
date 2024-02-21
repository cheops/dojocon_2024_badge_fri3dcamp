#include "tlv_screen.h"
#include <Badge2020_TFT.h>
#include <arpa/inet.h>

Badge2020_TFT tft;

bool begun = false;
void setup_screen() {
    if (!begun) {
        tft.init(240, 240);
        tft.setRotation( 2 );
    }
    begun = true;
}

void apply_screen_clear(const uint8_t *tlv_value)
{
    setup_screen();
    tft.fillScreen(ST77XX_BLACK);
}

void apply_screen_color(const uint8_t *tlv_value)
{
    // convert 2 bytes from network byte order to host byte order
    uint16_t color;
    memcpy(&color, tlv_value, sizeof(color));
    color = ntohs(color);

    setup_screen();
    tft.fillScreen(color);
}


static const uint8_t SCREEN_HEIGTH = 240;
static const uint8_t TEXT_SIZE = 3;
static uint8_t offset = 0;

void apply_screen_text(const uint8_t *tlv_value, const uint8_t tlv_length)
{
    if (offset >= SCREEN_HEIGTH)
    {
        offset = 0;
    }
    if (offset == 0)
    {
        tft.fillScreen(ST77XX_BLACK);
    }

    setup_screen();
    tft.setCursor(0, offset);
    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(TEXT_SIZE);
    String text(tlv_value, tlv_length);
    tft.print(text);
    
    offset += TEXT_SIZE * 8;
}
