#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#include "common.h"
#include "settings.h"

/**
 * disables hardware watchdog to prevent reset during busy wait in kernel module
 * @return 0 if successful, -1 if failed
 */
int disable_hw_watchdog() {
    // address and values taken from ar9331 datasheet
    int fd = open("/dev/mem", O_RDWR);
    void *ptr = mmap(NULL, 10, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0x18060000);
    close(fd);

    if (ptr == MAP_FAILED) {
        printf("mmap failed\n");
        return -1;
    }

    volatile unsigned *wd_addr = (unsigned *) (ptr + 0x8);  // address 0x18060008
    *wd_addr = 0x80000000;                                  // set bit[1:0] = 0 (datasheet 6.6.3)
    printf("disabled hardware watchdog\n");
    if (munmap(ptr, 10) < 0) {
        printf("munmap failed\n");
        return -1;
    }
    return 0;
}

/**
 * open and initialize device
 * disables hardware watchdog on ar9331 devices
 * @param fd file descriptor of char device
 * @param pin GPIO of LED
 * @param bit_time duration of one bit
 * @param guard_time delay between each byte sent
 * @param active_preamble 1 to send preamble
 * @return 0 if successful, <0 if failed
 */
int prepare_device(int fd, int pin, int bit_time, int guard_time, int active_preamble) {

#ifdef DISABLE_AR9331_WD
    if (disable_hw_watchdog() < 0) {
        printf("disabling hardware watchdog failed\n");
        return -1;
    }
#endif

    int ret = 0;
    int gpio[] = {GPIO, pin};
    printf("change pin to %d\n", gpio[1]);
    ret += common_io_call(fd, SETTING, (int *) gpio);

    int bit_dur[] = {BIT_DUR, bit_time};
    printf("change bit duration to %d\n", bit_dur[1]);
    ret += common_io_call(fd, SETTING, (int *) bit_dur);

    int guard[] = {GUARD, guard_time};
    printf("change guard time to %d\n", guard[1]);
    ret += common_io_call(fd, SETTING, (int *) guard);

    int preamble[] = {PREAMBLE, active_preamble};
    printf("change preamble to %d\n", preamble[1]);
    ret += common_io_call(fd, SETTING, (int *) preamble);

    if (ret < 0) {
        printf("error while ioctl\n");
        return -1;
    }

    return ret;
}

/**
 * read file and write to kernel module's char device
 * @param target file descriptor of char device
 * @param file input file name
 */
void read_write(int target, char *file) {
    // read source file to buffer
    FILE *source;
    source = fopen(file, "rb");
    if (source == NULL) {
        printf("error opening source file\n");
        return;
    }

    fseek(source, 0, SEEK_END);
    long src_size = ftell(source);
    fseek(source, 0, SEEK_SET);

    char *content = malloc(src_size + 1);
    fread(content, 1, src_size, source);
    fclose(source);

    content[src_size] = 0;

    // write to char device
    write(target, &content, src_size);
    printf("file transfer completed\n");
    free(content);
}

/**
 * prints usage information
 */
void print_usage() {
    printf("Usage: ./transmitter -p -g GUARD -b BIT_DUR -o PIN -f FILE \n\n"
           "arguments:                                                 \n"
           " -p activates preamble                                     \n"
           " -g GUARD guard time                                       \n"
           " -b BIT bit time                                           \n"
           " -o PIN gpio pin                                           \n"
           " -f FILE data to send                                      \n");
}

/**
 * main
 * @param argc command line arguments
 * @param argv command line arguments
 * @return 0 if successful, -1 if failed
 */
int main(int argc, char *argv[]) {
    int fd, opt;

    int f_flag = 0;

    int guard = 0;
    int bit = 10;
    int gpio = 112;
    int preamble = 0;
    char *file;

    while((opt = getopt(argc, argv, "pg:b:o:f:")) != -1) {
        switch (opt) {
            case 'p':
                preamble = 1;
                break;
            case 'g':
                guard = strtol(optarg, NULL, 10);
                break;
            case 'b':
                bit = strtol(optarg, NULL, 10);
                break;
            case 'o':
                gpio = strtol(optarg, NULL, 10);
                break;
            case 'f':
                file = optarg;
                if (file != NULL) {
                    f_flag = 1;
                }
                break;
            default:
                print_usage();
                return 0;
        }
    }

    if (f_flag == 1) {
        printf("guard=%d bit=%d gpio=%d preamble=%d file=%s\n", guard, bit, gpio, preamble, file);
        printf("write file...\n");
        int fd = common_open_device();
        if (fd == 0) {
            printf("error opening char device\n");
            return 1;
        }
        read_write(fd, file);
        printf("prepare device...\n");
        if (prepare_device(fd, gpio, bit, guard, preamble) != 0) {
            printf("failed to prepare the device");
            close(fd);
            return -1;
        }
        printf("transmitting data...\n");
        common_io_call(fd, TRANSMIT, NULL);
        close(fd);
    } else {
        printf("./transmitter: 'f' argument required\n");
        print_usage();
    }

    return 0;
}