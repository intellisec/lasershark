#ifndef COMMON_H
#define COMMON_H

/**
 * kernel module ioctl command defines
 * magic number, command number, argument
 */
#define STATUS _IOR(0x77, 0x00, int *)
#define MODE _IOW(0x77, 0x01, int *)
#define GET_SAMPLE _IOR(0x77, 0x02, int *)
#define RECEIVE _IOR(0x77, 0x03, int *)
#define SETTING _IOW(0x77, 0x04, int *)
#define MEASURE_LOAD _IOR(0x77, 0x05, int *)
#define TRANSMIT _IOR(0x77, 0x06, int *)
#define TRANSMIT_TEST _IOR(0x77, 0x07, int *)

/**
 * kernel module settings
 */
#define MAX_WAIT 0
#define CAP_LOAD 1
#define CAP_UNLOAD 2
#define GPIO 3
#define BUF_LEN 4
#define GUARD 5
#define BIT_DUR 6
#define PREAMBLE 7

/**
 * common.c prototypes
 */
int common_open_device(void);
int common_io_call(int fd, unsigned long request, int *value);
int common_init(int fd, int mode, int pin, int max_wait, int buffer_len, int load, int unload);
int common_start_receiving(int fd);
int common_read(int fd);
int common_measure(int fd, int min, int max, int length);
int common_decode(int fd, int min, int center, int max, int length, char *buffer, int buffer_len);
int common_measure_load_time(int fd);

#endif