#ifndef __STARTUP_TEMPLATE_H__
#define __STARTUP_TEMPLATE_H__

/** @brief APP_FAST_ADV between 0x0020 and 0x4000 in 0.625 ms units (20ms to 10.24s). */
#define APP_FAST_ADV						(1600)

/** @brief APP_ADV_TIMEOUT Advertising time-out between 0x0001 and 0x028F in seconds, 0x0000 disables time-out.*/
#define APP_ADV_TIMEOUT						(0x0000)
#define LED_Toggle(led_gpio)  gpio_pin_toggle_output_level(led_gpio)

#define COMPLETE_NAME						"ISIT"
#define COMPLETE_NAME_LENGTH				0x05

#define SENSOR_DATA_LENGTH					0x01

#define AD_TYPE_FIELD_LENGTH				0x01

#define SEAT_SERVICE_UUID1					0xbd33065997ce5163
#define SEAT_SERVICE_UUID2					0xc30db14495294580

#define SEAT_TOTAL_CHARACTERISTIC_NUM		1

#define SEAT_CHARACTERISTIC_UUID1			0xcdd772fddd624cee
#define SEAT_CHARACTERISTIC_UUID2			0xa2fad76dbee2045d

at_ble_status_t set_adv_data(bool value);
static void seat_primary_service_define(void);
bool seat_sensor_send_notification(void);

#endif /* __STARTUP_TEMPLATE_H__ */
