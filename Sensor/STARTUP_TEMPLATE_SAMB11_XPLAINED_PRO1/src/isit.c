/*- Includes ---------------------------------------------------------------*/
#include <asf.h>
#include "platform.h"
#include "at_ble_api.h"
#include "console_serial.h"
#include "timer_hw.h"
#include "ble_manager.h"
#include "ble_utils.h"
#include "button.h"
#include "led.h"
#include "gpio.h"
#include "samb11_xplained_pro.h"
#include "isit.h"
#include "adc_sam_b.h"

typedef struct seat_gatt_service_handler {
	/** service uuid */
	at_ble_uuid_t serv_uuid;
	/** service handle */
	at_ble_handle_t serv_handle;
	/** characteristic handle */
	at_ble_characteristic_t serv_chars[SEAT_TOTAL_CHARACTERISTIC_NUM];
} seat_gatt_service_handler_t;

bool value_changed = false;
bool sensor_value = false;
seat_gatt_service_handler_t seat_service_handler;
at_ble_handle_t connection_handle;

void io_init(void) 
{
	struct gpio_config config_gpio_pin;
	gpio_get_config_defaults(&config_gpio_pin);
	config_gpio_pin.direction = GPIO_PIN_DIR_OUTPUT;
	gpio_pin_set_config(OUTPUT_PIN, &config_gpio_pin);
}

at_ble_status_t set_adv_data(bool value)
{
	uint8_t adv_length = 0;
	uint8_t scan_rsp_data[0];
	uint8_t adv_data[31];
	//Complete name
	adv_data[adv_length++] = COMPLETE_NAME_LENGTH + AD_TYPE_FIELD_LENGTH;
	adv_data[adv_length++] = COMPLETE_LOCAL_NAME;
	memcpy((adv_data + adv_length), COMPLETE_NAME, COMPLETE_NAME_LENGTH);
	adv_length = adv_length + COMPLETE_NAME_LENGTH;
	//Service data
	adv_data[adv_length++] = 16 + AD_TYPE_FIELD_LENGTH;
	adv_data[adv_length++] = COMPLETE_LIST_128BIT_SERV_UUIDS;
	for(uint8_t i=0;i<8;i++) {
		adv_data[adv_length+i] = (uint8_t)(SEAT_SERVICE_UUID2>>i*8);
		adv_data[adv_length+i+8] = (uint8_t)(SEAT_SERVICE_UUID1>>i*8);
	}
	adv_length = adv_length + 16;

	if (at_ble_adv_data_set(adv_data, adv_length, scan_rsp_data, 0) != AT_BLE_SUCCESS) {
		DBG_LOG("BLE Broadcast data set failed");
		return AT_BLE_FAILURE;
		}else {
		DBG_LOG("BLE Broadcast data set successs");
	}
	return AT_BLE_SUCCESS;
}

static at_ble_status_t start_advertisement(void)
{
	/* Start of advertisement */
	if(at_ble_adv_start(AT_BLE_ADV_TYPE_UNDIRECTED, AT_BLE_ADV_GEN_DISCOVERABLE, \
		NULL, AT_BLE_ADV_FP_ANY, APP_FAST_ADV, APP_ADV_TIMEOUT, 0) == \
		AT_BLE_SUCCESS)
	{
		DBG_LOG("BLE Started Advertisement");
		return AT_BLE_SUCCESS;
	}
	else
	{
		DBG_LOG("BLE Advertisement start Failed");
	}
	return AT_BLE_FAILURE;
}


/* Callback functions */

/* Callback registered for AT_BLE_PAIR_DONE event from stack */
static at_ble_status_t ble_paired_app_event(void *param)
{
	//LED_On(LED0);
	seat_sensor_send_notification();
	ALL_UNUSED(param);
	return AT_BLE_SUCCESS;
}

/* Callback registered for AT_BLE_DISCONNECTED event from stack */
static at_ble_status_t ble_disconnected_app_event(void *param)
{
	set_adv_data(sensor_value);
	start_advertisement();
	LED_Off(LED0);
	ALL_UNUSED(param);
	return AT_BLE_SUCCESS;	
}

/* Callback registered for AT_BLE_CONNECTED event from stack */
static at_ble_status_t ble_connected_app_event(void *param)
{
	at_ble_connected_t *conn_params;
	conn_params = (at_ble_connected_t *)param;
	connection_handle = (at_ble_handle_t)conn_params->handle;
	ALL_UNUSED(param);
	return AT_BLE_SUCCESS;
}


/* Callback registered for AT_BLE_NOTIFICATION_CONFIRMED event from stack */
static at_ble_status_t ble_notification_confirmed_app_event(void *param)
{
	at_ble_cmd_complete_event_t *notification_status = (at_ble_cmd_complete_event_t *)param;
	if(!notification_status->status)
	{
		DBG_LOG_DEV("Notification sent successfully");
		return AT_BLE_SUCCESS;
	}
	return AT_BLE_FAILURE;
}

/* Callback registered for AT_BLE_CHARACTERISTIC_CHANGED event from stack */
static at_ble_status_t ble_char_changed_app_event(void *param)
{
	ALL_UNUSED(param);
	return AT_BLE_SUCCESS;
}

static const ble_event_callback_t startup_template_app_gap_cb[] = {
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	ble_connected_app_event,
	ble_disconnected_app_event,
	NULL,
	NULL,
	ble_paired_app_event,
	NULL,
	NULL,
	NULL,
	NULL,
	ble_paired_app_event,
	NULL,
	NULL,
	NULL,
	NULL
};

static const ble_event_callback_t startup_template_app_gatt_server_cb[] = {
	ble_notification_confirmed_app_event,
	NULL,
	ble_char_changed_app_event,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL
};
static void configure_adc(void)
{
	struct adc_config config_adc;
	adc_get_config_defaults(&config_adc);
	config_adc.input_channel = ADC_PIN;
	config_adc.input_dynamic_range = ADC_INPUT_DYNAMIC_RANGE_0;

	adc_init(&config_adc);

	adc_enable();
}

/* timer callback function */
static void timer_callback_fn(void)
{
	uint16_t result;
	configure_adc();
	while(adc_read(ADC_PIN, &result) == STATUS_BUSY) {
	}
	DBG_LOG("Result: %d", result);
	if(result > 1000) {
		gpio_pin_set_output_level(OUTPUT_PIN, true);
	} else {
		gpio_pin_set_output_level(OUTPUT_PIN, false);
	}
}

static void button_cb(void)
{
	sensor_value = !sensor_value;
	value_changed = true;
	if (sensor_value) {
		LED_On(LED0);
	} else {
		LED_Off(LED0);
	}
}

int main(void)
{
	platform_driver_init();
	acquire_sleep_lock();

	/* Initialize serial console */
	serial_console_init();
	system_clock_config(CLOCK_RESOURCE_XO_26_MHZ, CLOCK_FREQ_26_MHZ);
	/* Hardware timer */
	hw_timer_init();
	
	/* button initialization */
	button_init(button_cb);

	hw_timer_register_callback(timer_callback_fn);
	hw_timer_start(1);
	DBG_LOG("Initializing BLE Application");
	
	/* initialize the BLE chip  and Set the Device Address */
	ble_device_init(NULL);

	/* Register Primary/Included service in case of GATT Server */
	configure_adc();
	set_adv_data(sensor_value);
	/* set the advertisement data */
	seat_primary_service_define();
	/* Start the advertisement */
	start_advertisement();
	/* Register callbacks for gap related events */
	ble_mgr_events_callback_handler(REGISTER_CALL_BACK,
									BLE_GAP_EVENT_TYPE,
									startup_template_app_gap_cb);
	
	/* Register callbacks for gatt server related events */
	ble_mgr_events_callback_handler(REGISTER_CALL_BACK,
									BLE_GATT_SERVER_EVENT_TYPE,
									startup_template_app_gatt_server_cb);
	io_init();
	/* Intialize LED */
	led_init();
	LED_Off(LED0);
	uint16_t result = 0;
	while(true)
	{
		/* BLE Event task */
		ble_event_task(BLE_EVENT_TIMEOUT);

		if(value_changed) {
			at_ble_adv_stop();
			set_adv_data(sensor_value);
			start_advertisement();
			seat_sensor_send_notification();
			DBG_LOG("Sensor value updated: %d", sensor_value);
			value_changed = false;
		}
		
	}
	DBG_LOG("Ferdig");
}

static void seat_primary_service_define(void)
{
	at_ble_status_t status;
	seat_service_handler.serv_handle = 0;
	seat_service_handler.serv_uuid.type = AT_BLE_UUID_128;

	for(uint8_t i=0;i<8;i++) {
		seat_service_handler.serv_uuid.uuid[i] = (uint8_t)(SEAT_SERVICE_UUID2>>i*8);
		seat_service_handler.serv_uuid.uuid[i+8] = (uint8_t)(SEAT_SERVICE_UUID1>>i*8);
	}
	/* handle stored here */
	seat_service_handler.serv_chars[0].char_val_handle = 0;
	seat_service_handler.serv_chars[0].uuid.type = AT_BLE_UUID_128;

	for(uint8_t i=0;i<8;i++) {
		seat_service_handler.serv_chars[0].uuid.uuid[i] = (uint8_t)(SEAT_CHARACTERISTIC_UUID2>>i*8);
		seat_service_handler.serv_chars[0].uuid.uuid[i+8] = (uint8_t)(SEAT_CHARACTERISTIC_UUID1>>i*8);
	}

	/* Properties */
	seat_service_handler.serv_chars[0].properties = AT_BLE_CHAR_NOTIFY | AT_BLE_CHAR_READ; 

	seat_service_handler.serv_chars[0].init_value
	= (uint8_t *)&sensor_value;
	seat_service_handler.serv_chars[0].value_init_len = sizeof(uint8_t);

	seat_service_handler.serv_chars[0].value_max_len = 1;
	
	/* Permissions */
	seat_service_handler.serv_chars[0].value_permissions
	= AT_BLE_ATTR_NO_PERMISSIONS;
	
	/* user defined name */
	seat_service_handler.serv_chars[0].user_desc = NULL;
	seat_service_handler.serv_chars[0].user_desc_len = 0;
	seat_service_handler.serv_chars[0].user_desc_max_len =  0;
	/*user description permissions*/
	seat_service_handler.serv_chars[0].user_desc_permissions
	= AT_BLE_ATTR_NO_PERMISSIONS;
	
	/* client config permissions */
	#if BLE_PAIR_ENABLE
	seat_service_handler.serv_chars[0].client_config_permissions
	= (AT_BLE_ATTR_WRITABLE_REQ_AUTHN_NO_AUTHR);
	
	#else
	seat_service_handler.serv_chars[0].client_config_permissions
	= (AT_BLE_ATTR_NO_PERMISSIONS);
	#endif
	
	/*server config permissions*/
	seat_service_handler.serv_chars[0].server_config_permissions
	= AT_BLE_ATTR_NO_PERMISSIONS;
	/*user desc handles*/
	seat_service_handler.serv_chars[0].user_desc_handle = 0;
	/*client config handles*/
	seat_service_handler.serv_chars[0].client_config_handle = 0;
	/*server config handles*/
	seat_service_handler.serv_chars[0].server_config_handle = 0;
	/* presentation format */
	seat_service_handler.serv_chars[0].presentation_format = NULL;
	status = at_ble_primary_service_define(&seat_service_handler.serv_uuid, &seat_service_handler.serv_handle, NULL, 0,
	seat_service_handler.serv_chars, SEAT_TOTAL_CHARACTERISTIC_NUM);
	if ( status != AT_BLE_SUCCESS) {
			DBG_LOG("Seat Service definition Failed,reason: %x",
			status);
			} else {
			DBG_LOG("Seat service defined succesfully");
	}
}

bool seat_sensor_send_notification(void)
{
	at_ble_status_t status;
	
	/** Updating the new characteristic value */
	if ((status = at_ble_characteristic_value_set(
	seat_service_handler.serv_chars[0].char_val_handle,
	(uint8_t*)&sensor_value, SENSOR_DATA_LENGTH)) != AT_BLE_SUCCESS) {
		DBG_LOG("Write value for notification failed,reason %d",
		status);
		return false;
	}

	/** Sending the notification for the updated characteristic */
	if ((status	= at_ble_notification_send(connection_handle,
	seat_service_handler.serv_chars[0]
	.char_val_handle))) {
		DBG_LOG("Send notification failed,reason %d", status);
		return false;
	}
	
	return true;
}
