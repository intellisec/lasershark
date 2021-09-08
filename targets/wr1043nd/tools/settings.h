#ifndef SETTINGS_H
#define SETTINGS_H

// tested with green laser pointer
// zero: 200us
// one: 400us
// guard: 100us
// bitrate: 2 kBit/s
// ./receiver -d 250 (on wr1043nd)
// sudo python3 send.py -m 2 -d /dev/ttyACM0 -t

#define GPIO_PIN 5
#define REC_MODE 0
#define BIT_BUFFER_LENGTH 16000
#define MIN_DUR 30
#define MAX_DUR 10000
#define CAP_LOAD_TIME 5
#define CAP_UNLOAD_TIME 5

#define DISABLE_AR9331_WD

#endif
