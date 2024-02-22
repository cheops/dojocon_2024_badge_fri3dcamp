#include <Arduino.h>

#include <tlv_pixels.h>
#include <tlv_buzzer.h>
#include <tlv_screen.h>

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

int scanTime = 5; // In seconds
BLEScan *pBLEScan;

static const std::string wanted_manufacturer_id = "\xff\xff";

// put function declarations here:
void parse_manufacturer_data(const uint8_t *data, const size_t length);
esp_err_t check_length(const uint8_t expected_length, const uint8_t tlv_length);
esp_err_t apply_tlv(const uint8_t tlv_type, const uint8_t tlv_length, const uint8_t *tlv_value);

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks
{
    void onResult(BLEAdvertisedDevice advertisedDevice)
    {
        if (advertisedDevice.haveManufacturerData())
        {

            // char *pHex = BLEUtils::buildHexData(nullptr, (uint8_t*)advertisedDevice.getManufacturerData().data(), advertisedDevice.getManufacturerData().length());
            // log_i("address: %s, manufacturer_data: %s", advertisedDevice.getAddress().toString().c_str(), pHex);
            // free(pHex);

            if (advertisedDevice.getManufacturerData().length() < 2)
            {
                log_d("skipping, not enough manufacturer data");
                return;
            }

            if (advertisedDevice.getManufacturerData().substr(0, 2) != wanted_manufacturer_id)
            {
                log_d("skipping, wrong manufacturer");
                return;
            }

            const uint8_t *data_array = reinterpret_cast<const uint8_t *>(advertisedDevice.getManufacturerData().data());
            size_t data_length = advertisedDevice.getManufacturerData().length();
            // strip manufacurer_id
            data_array = data_array + 2;
            data_length = data_length - 2;

            parse_manufacturer_data(data_array, data_length);
        }
    }
};

void setup()
{
    // put your setup code here, to run once:
    Serial.begin(115200);
    log_i(":: setup");

    BLEDevice::init("");
    pBLEScan = BLEDevice::getScan();                                                 // create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks(), true); // true: want duplicates
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(99); // less or equal setInterval value
}

void loop()
{
    // put your main code here, to run repeatedly:
    log_i(":: loop");

    BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
    pBLEScan->clearResults(); // delete results fromBLEScan buffer to release memory

    delay(20);
}

uint8_t last_tlv_type = 0;
uint8_t last_tlv_length = 0;
uint8_t *last_tlv_value = nullptr;

// put function definitions here:
void parse_manufacturer_data(const uint8_t *data_array, const size_t data_length)
{
    size_t current_pos = 0;

    while (current_pos + 2 <= data_length)
    {

        const uint8_t tlv_type = data_array[current_pos + 0];
        const uint8_t tlv_length = data_array[current_pos + 1];

        if ((current_pos + 2 + tlv_length) > data_length)
        {
            log_e("data_length too short");
            return;
        }

        // check if different from last tlv
        bool tlv_type_same = (last_tlv_type == tlv_type);
        bool tlv_length_same = (last_tlv_length == tlv_length);
        bool tlv_value_same = false;
        if ((last_tlv_value == nullptr && tlv_length == 0) ||
            (last_tlv_value != nullptr && memcmp(last_tlv_value, data_array + current_pos + 2, tlv_length) == 0))
        {
            tlv_value_same = true;
        };
        if (tlv_type_same && tlv_length_same && tlv_value_same)
        {
            log_d("skipping, same as last tlv");
            return;
        }

        uint8_t *tlv_value = nullptr;
        if (tlv_length > 0)
        {
            // remember to free tlv_value after use, this is done after it has been stored in last_tlv_value
            tlv_value = reinterpret_cast<uint8_t *>(ps_malloc(tlv_length * sizeof(uint8_t)));
            if (tlv_value == nullptr)
            {
                log_e("failed to allocate memory for tlv_value");
                return;
            }
            memcpy(tlv_value, data_array + current_pos + 2, tlv_length);
        }

        Serial.printf("tlv_type: %u, tlv_length: %u, tlv_value: ", tlv_type, tlv_length);
        log_buf_e(tlv_value, tlv_length);
        if (tlv_value == nullptr)
            Serial.println();

        esp_err_t ret = apply_tlv(tlv_type, tlv_length, tlv_value);
        if (ret != ESP_OK) {
            log_e("there was an error: %d", ret);
        }

        // different from last, so save it
        last_tlv_type = tlv_type;
        last_tlv_length = tlv_length;
        free(last_tlv_value);
        last_tlv_value = tlv_value;

        current_pos = current_pos + 2 + tlv_length;
    }

    if (current_pos != data_length)
    {
        log_e("remaining bytes cannot be parsed");
    }
}

esp_err_t check_length(const uint8_t expected_length, const uint8_t tlv_length)
{
    if (expected_length != tlv_length)
    {
        log_e("tlv_length failure, expected: %u, got %u", expected_length, tlv_length);
        return ESP_FAIL;
    }
    return ESP_OK;
}

esp_err_t apply_tlv(const uint8_t tlv_type, const uint8_t tlv_length, const uint8_t *tlv_value)
{
    esp_err_t ret = ESP_OK;
    switch (tlv_type)
    {
    case tlv_type_pixels_clear:
        ret = check_length(0, tlv_length);
        if (ret == ESP_OK)
        {
            apply_pixels_clear(tlv_value);
        }
        break;

    case tlv_type_pixels_set_color:
        ret = check_length(3, tlv_length);
        if (ret == ESP_OK)
        {
            apply_pixels_set_color(tlv_value);
        }
        break;

    case tlv_type_pixels_set_i_color:
        ret = check_length(4, tlv_length);
        if (ret == ESP_OK)
        {
            apply_pixels_set_i_color(tlv_value);
        }
        break;

    case tlv_type_pixels_set_5_color:
        ret = check_length(15, tlv_length);
        if (ret == ESP_OK)
        {
            apply_pixels_set_5_color(tlv_value);
        }
        break;

    case tlv_type_screen_clear:
        ret = check_length(0, tlv_length);
        if (ret == ESP_OK)
        {
            apply_screen_clear(tlv_value);
        }
        break;

    case tlv_type_screen_color:
        ret = check_length(2, tlv_length);
        if (ret == ESP_OK)
        {
            apply_screen_color(tlv_value);
        }
        break;

    case tlv_type_screen_text:
        apply_screen_text(tlv_value, tlv_length);
        break;

    case tlv_type_buzzer_note:
        ret = check_length(8, tlv_length);
        if (ret == ESP_OK)
        {
            apply_buzzer_note(tlv_value);
        }
        break;

    case tlv_type_buzzer_song:
        ret = check_length(1, tlv_length);
        if (ret == ESP_OK)
        {
            apply_buzzer_song(tlv_value);
        }
        break;

    default:
        log_e("unkown tlv_type: %u", tlv_type);
    }
    return ret;
}
