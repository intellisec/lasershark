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
 * decode and write received data to file
 * @param fd character device
 * @param length number of received bits
 * @param center decision threshold
 * @param file_name of output file
 * @return 0 if successful, -1 if failed
 */
int receive_file(int fd, int length, int center, char *file_name) {
    char *buffer = calloc(length, sizeof(char));
    if (common_decode(fd, MIN_DUR, center, MAX_DUR, length, buffer, length) < 0) {
        close(fd);
        return -1;
    }
    close(fd);

    // write to file
    FILE *file = fopen(file_name, "w");
    int ret = fputs(buffer, file);
    fclose(file);
    if (ret == EOF) {
        printf("couldn't write to file\n");
        return -1;
    }
    return 0;
}

/**
 * decode and write received data to stdout
 * @param fd character device
 * @param length number of received bits
 * @param center decision threshold
 * @return 0 if successful, -1 if failed
 */
int receive_stdout(int fd, int length, int center) {
    char *buffer = calloc(length, sizeof(char));
    if (common_decode(fd, MIN_DUR, center, MAX_DUR, length, buffer, length) > 0) {
        printf("%s\n", buffer);
        close(fd);
        return 0;
    };
    close(fd);
    return -1;
}

/**
 * open and initialize device
 * disables hardware watchdog on ar9331 devices
 * @param max_wait maximum time to wait for another bit
 * @return fd if successful, -1 if failed
 */
int prepare_device(int max_wait) {
    int fd;

#ifdef DISABLE_AR9331_WD
    if (disable_hw_watchdog() < 0) {
        printf("disabling hardware watchdog failed\n");
        return -1;
    }
#endif

    fd = common_open_device();
    if (common_init(fd, REC_MODE, GPIO_PIN, max_wait, BIT_BUFFER_LENGTH, CAP_LOAD_TIME, CAP_UNLOAD_TIME) < 0) {
        return -1;
    }
    return fd;
}

/**
 * prints usage information
 */
void print_usage() {
    printf("Usage: receiver (-m | -d | -l | -f FILE) CENTER\n\n"
           "arguments:                                       \n"
           " -m measurement                                  \n"
           " -d write data to stdout                         \n"
           " -f FILE write data to file                      \n"
           " -l measure capacitor load time                  \n"
           " CENTER time to decide between 0 and 1           \n");
}

/**
 * main
 * @param argc command line arguments
 * @param argv command line arguments
 * @return 0 if successful, -1 if failed
 */
int main(int argc, char *argv[]) {
    int fd, length, opt, center;
    int m_flag, d_flag, f_flag, l_flag = 0;
    char *p;

    while((opt = getopt(argc, argv, "mdlf:")) != -1) {
        switch(opt) {
            case 'm':
                m_flag = 1;
                break;
            case 'd':
                d_flag = 1;
                break;
            case 'f':
                f_flag = 1;
                break;
            case 'l':
                l_flag = 1;
                break;
            default:
                // missing argument
                print_usage();
                return 0;
        }

        if (argv[optind] == NULL) {
            print_usage();
            printf("Error: CENTER value required\n");
            return -1;
        }

        // required arguments set
        center = strtol(argv[optind], &p, 10);
        fd = prepare_device(center * 3);
        if (fd < 0) {
            return -1;
        }

        if (l_flag == 1) {
            int ret = common_measure_load_time(fd);
            close(fd);
            return ret;
        }

        length = common_start_receiving(fd);
        if (length < 0) {
            close(fd);
            return -1;
        }

        if (d_flag == 1) {
            printf("start receiving\n");
            return receive_stdout(fd, length, center);
        } else if (f_flag == 1) {
            printf("write data to: %s\n", optarg);
            return receive_file(fd, length, center, optarg);
        } else {
            printf("start measurement\n");
            return common_measure(fd, MIN_DUR, MAX_DUR, length);
        }
    }
    // no arguments
    print_usage();
    return 0;
}