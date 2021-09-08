#ifndef SETTINGS_H
#define SETTINGS_H

// no mininmal current needed, we can load the capacitor slowly

// working example for 1uA LED current
/**
#define GPIO_PIN 112
#define REC_MODE 1
#define BIT_BUFFER_LENGTH 8000
#define MIN_DUR 20
#define MAX_DUR 1000000
#define CAP_LOAD_TIME 19000
#define CAP_UNLOAD_TIME 20
**/

// working example for 24uA LED current
#define GPIO_PIN 112
#define REC_MODE 1
#define BIT_BUFFER_LENGTH 8000
#define MIN_DUR 10
#define MAX_DUR 1000000
#define CAP_LOAD_TIME 120
#define CAP_UNLOAD_TIME 20

#endif
