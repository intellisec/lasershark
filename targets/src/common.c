#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>

#include "common.h"

/**
 * open character device
 * @return descriptor
 */
int common_open_device(void) {
    int fd = open("/dev/led_transceiver", O_RDWR);
    return fd;
}

/**
 * calls ioctl handler of kernel module
 * @param fd character device
 * @param request command
 * @param value argument
 * @return 0 if successful
 */
int common_io_call(int fd, unsigned long request, int *value) {
    if (ioctl(fd, request, value) < 0) {
        printf("ioctl failed\n");
        return -1;
    }
    return 0;
}

/**
 * initializes kernel module
 * @param fd character device
 * @param mode 0 = resistor, 1 = capacitor
 * @param pin GPIO with LED
 * @param max_wait maximum bit duration
 * @param buffer_len length of kernel modules bit_buffer (if there is little memory available)
 * @return 0 if successful
 */
int common_init(int fd, int mode, int pin, int max_wait, int buffer_len, int load, int unload) {
    int ret = 0;
    printf("change mode to %d\n", mode);
    ret += common_io_call(fd, MODE, (int *) &mode);

    int gpio[] = {GPIO, pin};
    printf("change pin to %d\n", gpio[1]);
    ret += common_io_call(fd, SETTING, (int *) gpio);

    int max[] = {MAX_WAIT, max_wait};
    printf("change maximum wait bit duration to %d\n", max[1]);
    ret += common_io_call(fd, SETTING, (int *) max);

    int len[] = {BUF_LEN, buffer_len};
    printf("set bit buffer length to %d\n", len[1]);
    ret += common_io_call(fd, SETTING, (int *) len);

    int cap_load[] = {CAP_LOAD, load};
    printf("set capacitor load time to %d\n", cap_load[1]);
    ret += common_io_call(fd, SETTING, (int *) cap_load);

    int cap_unload[] = {CAP_UNLOAD, unload};
    printf("set capacitor unload time to %d\n", cap_unload[1]);
    ret += common_io_call(fd, SETTING, (int *) cap_unload);

    // print settings to kernel log
    ret += common_io_call(fd, STATUS, NULL);

    return ret;
}

/**
 * measures capacitor load time and builds average
 * @param fd character device
 * @return 0 if successful, -1 if failed
 */
int common_measure_load_time(int fd) {
    int sum = 0;
    int value = 0;
    int counter = 0;
    int global_min = 10000000;
    int global_max = 0;

    for (int i = 0; i < 10; i++) {
        if (common_io_call(fd, MEASURE_LOAD, &value) < 0) {
            return -1;
        }
        sum += value;
        counter++;
        if (global_max < value) {
            global_max = value;
        }
        if (global_min > value) {
            global_min = value;
        }
    }

    if (counter == 0) {
        printf("no samples received\n");
    } else {
        printf("min: %d\n", global_min);
        printf("max: %d\n", global_max);
        printf("length: %d\n", counter);
    }
    return 0;
}

/**
 * start receiving procedure
 * blocking for min. 30 secs
 * @param fd character device
 * @return number of received bits if successful, -1 if failed
 */
int common_start_receiving(int fd) {
    printf("waiting for data...\n");
    int length = 0;
    if (common_io_call(fd, RECEIVE, &length) < 0) {
        return -1;
    }
    return length;
}

/**
 * retrieve duration of one bit
 * @param fd character device
 * @return duration if successful, -1 if failed
 */
int common_read(int fd) {
    long long value;
    if (read(fd, &value, 8) < 8) {
        printf("error while reading from device\n");
        return -1;
    }
    //printf("value: %lld\n", value);
    // typecasting shouldn't be a problem as the durations are relatively small
    return (int)value;
}

/**
 * measure minima, maxima and average duration of received bits and print them
 * useful for calibrating sender and receiver
 * @param fd character device
 * @param min considered bit duration
 * @param max considered bit duration
 * @param length number of received bits
 * @return always 0
 */
int common_measure(int fd, int min, int max, int length) {
    int sum = 0;
    int value = 0;
    int counter = 0;
    int global_min = max;
    int global_max = min;

    for (int i = 0; i < length; i++) {
        value = common_read(fd);
        if (min < value && value < max) {
            //printf("value: %d\n", value);
            sum += value;
            counter++;
            if (global_max < value) {
                global_max = value;
            }
            if (global_min > value) {
                global_min = value;
            }
        }
    }

    if (counter == 0) {
        printf("no samples received\n");
    } else {
        printf("min: %d\n", global_min);
        printf("max: %d\n", global_max);
        printf("length: %d\n", counter);
    }
    return 0;
}

/**
 * decides if bit is 0 or 1, builds bytes and writes them to buffer
 * @param fd character device
 * @param min considered bit duration
 * @param center decision threshold
 * @param max considered bit duration
 * @param length number of received bits
 * @param buffer to store decoded bytes
 * @param buffer_len length of buffer
 * @return number of written bytes
 */
int common_decode(int fd, int min, int center, int max, int length, char *buffer, int buffer_len) {
    int value = 0;
    int b_count = 0;
    int c_count = 0;

    for (int i = 0; i < length; i++) {
        value = common_read(fd);
        if (min < value && value < max) {
            //printf("value: %d\n", value);
            if (value > center) {
                // 1
                buffer[c_count] |= 1 << (7 - b_count);
            } else {
                // 0
                buffer[c_count] |= 0 << (7 - b_count);
            }
            if (b_count == 7) {
                b_count = 0;
                c_count++;
            } else {
                b_count++;
            }
        } else {
            // out of range
            value = 0;
        }
        if (c_count == buffer_len) {
            printf("buffer was too small\n");
            return c_count;
        }
    }
    return c_count;
}