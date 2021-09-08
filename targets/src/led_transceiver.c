#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/ioctl.h>
#include <linux/string.h>
#include <linux/gpio.h>
#include <linux/irqflags.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/version.h>
#include "common.h"

#define MODULE_NAME "LED Transceiver"
#define LOG MODULE_NAME ": "
#define CHAR_NAME "led_transceiver"

#if LINUX_VERSION_CODE <= KERNEL_VERSION(3,4,20)
#include <linux/hrtimer.h>  // ancient t21p kernel
#else
#include <linux/timer.h>   // newer kernel
#endif

int gpio_pin = -1;

/**
 * received data
 */
int write_counter = 0;                  // number of measured bits (after receive_chunk())
int read_counter = 0;                   // number of already read bits (after dev_read())
s64 *bit_buffer = NULL;                 // array with measured bit durations
int (*get_sample_ptr)(void) = NULL;     // function pointer to selected get_sample method

/**
 * receiver settings
 */
int max_duration = 7000;                // maximum duration of one bit
int mode = 0;                           // there are two modes: 0 resistor only (mr3020), 1 resistor + capacitor (t21p)
int cap_load = 1000;                    // max time to load the capacitor (changes with different power)
int cap_unload = 20;                    // max time to unload the capacitor (should be always the same)
int bit_buffer_len = 80000;             // length of buffer to store measured durations (sizeof(s64) * bit_buffer_len)

/**
 * transmit data
 */
char *transmit_buffer;                  // storage for data to transmit
int transmit_length = 0;                // length of transmit data

/**
 * transmitter settings
 */
int bit_dur = 0;                        // bit duration
int guard = 0;                          // guard duration
int preamble = 0;                       // enable or disable preamble
int custom_delay = 0;                   // which delay should be used

/**
 * set gpio as output
 */
void gpio_out(void) {
    printk(KERN_ERR LOG "set gpio as output");
    if (gpio_direction_output(gpio_pin, 0) < 0) {
        printk(KERN_ERR LOG "couldn't set direction output gpio %d (led)\n", gpio_pin);
    }
}

/**
 * set gpio as input
 */
void gpio_in(void) {
    printk(KERN_ERR LOG "set gpio as input");
    if (gpio_direction_input(gpio_pin) < 0) {
        printk(KERN_ERR
        LOG "couldn't set direction input gpio %d (led)\n", gpio_pin);
    }
}

/**
 * initialize gpio pin
 */
int init_gpio(void) {
    // init gpio
    // may be used by other module, free it first
    printk(KERN_ERR LOG "init gpio %d", gpio_pin);
    gpio_free(gpio_pin);

    // request them
    if (gpio_request(gpio_pin, "green_led") < 0) {
        printk(KERN_ERR LOG "couldn't request gpio %d (led)\n", gpio_pin);
        return -1;
    }

    printk(KERN_INFO LOG "set gpio pin to %d\n", gpio_pin);
    return 0;
}

/**
 * returns one sample from LED
 * 1. capacitor between GPIO and GND
 * 2. resistor between GPIO and LED
 * 3. GPIO pin in HIGH-Z input mode
 * @return 0 or 1
 */
int get_sample_cap(void) {
    gpio_direction_output(gpio_pin, 0);
    // wait for capacitor to unload
    udelay(cap_unload);
    gpio_direction_input(gpio_pin);
    // wait for capacitor to load
    udelay(cap_load);
    return gpio_get_value(gpio_pin);
}

/**
 * returns one sample from LED
 * 1. resistor between GPIO and LED
 * 2. GPIO pin in PULL-DOWN mode
 * @return 0 or 1
 */
int get_sample_res(void) {
    return gpio_get_value(gpio_pin);
}

/**
 * measure time of each received bit and save it
 * blocking for min. 30 secs
 * @return number of written timestamps
 */
int receive_chunk(void) {
    unsigned long flags;
    int state;
    int sample;
    ktime_t start;
    s64 time_diff;

    if (gpio_pin < 0) {
        printk(KERN_ERR LOG "no gpio pin set\n");
        return 0;
    }

    gpio_in();

    // if buffer is not empty, clear it
    if (bit_buffer != NULL) {
        kfree(bit_buffer);
        bit_buffer = NULL;
        printk(KERN_INFO LOG "free bit_buffer\n");
    }

    bit_buffer = (s64 *) kmalloc(sizeof(s64) * bit_buffer_len, GFP_ATOMIC);
    if (bit_buffer == NULL) {
        printk(KERN_ERR LOG "couldn't allocate space\n");
        return 0;
    }

    printk(KERN_INFO LOG "waiting for data\n");
    // disable interrupts and stop scheduler
    local_irq_save(flags);

    write_counter = 0;
    read_counter = 0;
    state = 0;
    time_diff = 0;

    // wait 20 secs for first 1
    start = ktime_get();
    while (get_sample_ptr() == 0 && time_diff < 20000000) {
        time_diff = ktime_to_us(ktime_sub(ktime_get(), start));
    }
    time_diff = 0;
    start = ktime_get();
    state = 1;

    // wait 2 * maximum duration of bits or guard time until stop listening
    while (time_diff < max_duration * 2) {
        time_diff = ktime_to_us(ktime_sub(ktime_get(), start));
        sample = get_sample_ptr();
        if (sample == 0 && state == 1) {
            bit_buffer[write_counter] = time_diff;
            state = 0;
            write_counter++;
            if (write_counter == bit_buffer_len) {
                printk(KERN_ERR LOG "bit_buffer overflow detected\n");
                break;
            }
        } else if (sample == 1 && state == 0) {
            start = ktime_get();
            state = 1;
        }
    }

    // enable interrupts again
    local_irq_restore(flags);
    return write_counter;
}

/**
 * measures time to load the capacitor
 * @return time in us if successful, -1 if failed
 */
int measure_load(void) {
    ktime_t start;
    s64 time_diff = -1;

    if (gpio_pin < 0) {
        printk(KERN_ERR LOG "no gpio pin set\n");
        return -1;
    }

    gpio_in();

    // wait for capacitor to unload
    gpio_direction_output(gpio_pin, 0);
    udelay(cap_unload);

    // wait for gpio pin to get high
    start = ktime_get();
    gpio_direction_input(gpio_pin);

    // wait max 20 secs
    while (gpio_get_value(gpio_pin) == 0 && time_diff < 20000000) {
        time_diff = ktime_to_us(ktime_sub(ktime_get(), start));
    }

    if (time_diff >= 30000) {
        return -1;
    }

    // typecast shouldn't be a problem as the time to measure is small
    return time_diff;
}

/**
 * transmits data
 * @return number of sent bytes
 */
int transmit_chunk(void) {
    unsigned long flags;
    int counter = 0;
    int i, j;

    if (gpio_pin < 0) {
        printk(KERN_ERR LOG "no gpio pin set\n");
        return 0;
    }

    // if buffer is empty abort
    if (transmit_buffer == NULL) {
        printk(KERN_INFO LOG "data_buffer is empty\n");
        return 0;
    }

    gpio_out();

    printk(KERN_INFO LOG "transmitting data\n");
    // disable interrupts and stop scheduler
    local_irq_save(flags);

    // send preamble
    if (preamble == 1) {
        char c = 0xAA;
        for (i = 7; i > -1; i--) {
            int bit = (c >> i) & 1;
            gpio_set_value(gpio_pin, bit);
            udelay(bit_dur);
        }

        if (guard > 0) {
            gpio_set_value(gpio_pin, 0);
            udelay(guard);
        }
    }

    // send actual data
    for (j = 0; j < transmit_length; j++) {
        char c = transmit_buffer[j];
        for (i = 7; i > -1; i--) {
            int bit = (c >> i) & 1;
            gpio_set_value(gpio_pin, bit);
            udelay(bit_dur);
        }

        if (guard > 0) {
            gpio_set_value(gpio_pin, 0);
            udelay(guard);
        }
        counter++;
    }
    gpio_set_value(gpio_pin, 0);

    // enable interrupts again
    local_irq_restore(flags);

    // free buffer
    kfree(transmit_buffer);
    transmit_length = 0;
    return counter;
}

/**
 * transmits 100 x 16 bit test sequence
 * interval = 2ms
 * @return number of sent bytes
 */
int transmit_test(void) {
    int i, j;
    unsigned long flags;

    if (gpio_pin < 0) {
        printk(KERN_ERR LOG "no gpio pin set\n");
        return 0;
    }

    gpio_out();

    printk(KERN_INFO LOG "transmitting test sequence\n");
    local_irq_save(flags);

    for (j = 0; j < 100; j++) {
        for (i = 0; i < 8; i++) {
            gpio_set_value(gpio_pin, 1);
            udelay(bit_dur);
            gpio_set_value(gpio_pin, 0);
            udelay(bit_dur);
        }
        udelay(2000);
    }

    local_irq_restore(flags);
    return 200;
}

/**
 * ioctl handler
 * @param file device file
 * @param cmd ioctl command
 * @param arg pointer to userspace
 * @return 0 if successful
 */
static long dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg) {
    int data[2];
    int ret = -1;

    switch (cmd) {
        case STATUS:
            // print current settings in kernel log
            data[0] = 1;
            printk(KERN_INFO LOG "settings:\nmax_duration = %d\nmode = %d\ngpio = %d\ncap_load = %d\ncap_unload = %d\n"
                                 "bit_buffer = %d\nbit_dur = %d\nguard=%d", max_duration, mode, gpio_pin, cap_load,
                                 cap_unload, bit_buffer_len, bit_dur, guard);
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
        case MODE:
            // change mode how to get samples
            ret = copy_from_user(&data, (int *)arg, sizeof(int));
            if (data[0] == 0) {
                // only resistor mode
                mode = 0;
                get_sample_ptr = &get_sample_res;
                printk(KERN_INFO LOG "changed mode to resistor only (%d)\n", *data);
            } else if (data[0] == 1) {
                // resistor and capacitor mode
                mode = 1;
                get_sample_ptr = &get_sample_cap;
                printk(KERN_INFO LOG "changed mode to resistor and capacitor (%d)\n", *data);
            } else {
                printk(KERN_ERR LOG "changing mode failed\n");
            }
            break;
        case GET_SAMPLE:
            // get one sample, returns sample value
            data[0] = get_sample_ptr();
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
        case RECEIVE:
            // start receiving procedure, returns length of received symbols
            data[0] = receive_chunk();
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
        case TRANSMIT:
            // start receiving procedure, returns length of received symbols
            data[0] = transmit_chunk();
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
        case TRANSMIT_TEST:
            // start receiving procedure, returns length of received symbols
            data[0] = transmit_test();
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
        case SETTING:
            // change specific setting, arg is int[2] = {property, value}
            ret = copy_from_user(&data, (int *)arg, sizeof(int) * 2);
            switch (data[0]) {
                case MAX_WAIT:
                    max_duration = data[1];
                    break;
                case CAP_LOAD:
                    cap_load = data[1];
                    break;
                case CAP_UNLOAD:
                    cap_unload = data[1];
                    break;
                case GPIO:
                    gpio_pin = data[1];
                    init_gpio();
                    break;
                case BUF_LEN:
                    bit_buffer_len = data[1];
                    break;
                case BIT_DUR:
                    bit_dur = data[1];
                    break;
                case GUARD:
                    guard = data[1];
                    break;
                case PREAMBLE:
                    preamble = data[1];
                    break;
                default:
                    printk(KERN_ERR LOG "unknown setting\n");
            }
            printk(KERN_INFO LOG "setting changed to %d\n", data[1]);
            break;
        case MEASURE_LOAD:
            // measure time to load the capacitor
            data[0] = measure_load();
            ret = copy_to_user((int *)arg, &data, sizeof(int));
            break;
    }
    return ret;
}

/**
 * character device
 */
dev_t char_dev = 0;
static struct class *dev_class;
static struct cdev dev_cdev;

/**
 * called when device file gets opened
 * @param inode
 * @param file
 * @return 0 if successful
 */
static int dev_open(struct inode *inode, struct file *file) {
    if (gpio_pin != -1) {
        init_gpio();
    }
    printk(KERN_INFO LOG "device open\n");
    return 0;
}

/**
 * called when device file gets closed
 * @param inode
 * @param file
 * @return 0 if successful
 */
static int dev_release(struct inode *inode, struct file *file) {
    gpio_free(gpio_pin);
    // if buffer is not empty, clear it
    if (bit_buffer != NULL) {
        kfree(bit_buffer);
        bit_buffer = NULL;
        printk(KERN_INFO LOG "free bit_buffer\n");
    }
    printk(KERN_INFO LOG "device close\n");
    return 0;
}

/**
 * called while reading from device file
 * @param file
 * @param userbuff buffer in userspace
 * @return number of copied bytes or -1 if failed
 */
static ssize_t dev_read(struct file *file, char __user *userbuff, size_t len, loff_t *off) {
    int ret = 0;
    int read_bytes = 0;
    int old_read_counter = read_counter;

    // check if bit buffer is filled
    if (bit_buffer == NULL) {
        printk(KERN_ERR LOG "haven't received any data yet\n");
        return 0;
    }

    // copy bit_buffer to userbuffer based on already read bytes and userbuffer length
    if ((write_counter - read_counter) * 8 <= len) {
        printk(KERN_INFO LOG "read complete bit_buffer");
        ret = copy_to_user(userbuff, bit_buffer + read_counter, (write_counter - read_counter) * 8);
        read_bytes = (write_counter - read_counter) * 8;
        read_counter = write_counter;
    } else {
        printk(KERN_INFO LOG "read %d bytes of bit_buffer", len);
        ret = copy_to_user(userbuff, bit_buffer + read_counter, len);
        read_counter = read_counter + (len / 8);
        read_bytes = len;
    }

    if (read_counter > write_counter - 1) {
        kfree(bit_buffer);
        bit_buffer = NULL;
    }

    if (ret != 0) {
        printk(KERN_ERR LOG "couldn't copy data to userspace\n");
        read_counter = old_read_counter;
        return -1;
    }

    return read_bytes;
}

/**
 * called while writing to device file
 * does nothing
 * @param file
 * @param __user
 * @return length of written data
 */
static ssize_t dev_write(struct file *file, const char __user *userbuff, size_t len, loff_t *off) {
    int error_count = 0;

    printk(KERN_INFO LOG "write called\n");
    transmit_length = len;
    transmit_buffer = (char *) kmalloc(sizeof(char) * transmit_length, GFP_ATOMIC);
    if (transmit_buffer == NULL) {
        printk(KERN_ERR LOG "couldn't allocate space\n");
        return 0;
    }

    error_count = copy_from_user(transmit_buffer, userbuff, transmit_length);
    if (error_count > 0) {
        printk(KERN_ERR LOG "couldn't copy data to kernel\n");
        return 0;
    }

    printk(KERN_INFO LOG "transmit_length: %d", transmit_length);
    //printk(KERN_INFO LOG "data: %.*s\n", transmit_length, transmit_buffer);

    return len;
}

/**
 * structure for device initialization
 */
static struct file_operations file_ops = {
        .owner          = THIS_MODULE,
        .read           = dev_read,
        .write          = dev_write,
        .open           = dev_open,
        .unlocked_ioctl = dev_ioctl,
        .release        = dev_release,
};

/**
 * initializes and registers character device
 */
static int __init mod_init(void) {
    // register char device numbers (major and minor) and name
    if (alloc_chrdev_region(&char_dev, 0, 1, CHAR_NAME) < 0) {
        printk(KERN_ERR LOG "couldn't register device number\n");
        return -1;
    }

    // initialize char device struct with functions
    cdev_init(&dev_cdev, &file_ops);

    // add char device to system
    if (cdev_add(&dev_cdev, char_dev, 1) < 0) {
        printk(KERN_ERR LOG "couldn't add device to system\n");
        unregister_chrdev_region(char_dev, 1);
        return -1;
    }

    // create /sys/class entry
    dev_class = class_create(THIS_MODULE, CHAR_NAME);
    if (dev_class == NULL) {
        printk(KERN_ERR LOG "couldn't create class\n");
        unregister_chrdev_region(char_dev, 1);
        return -1;
    }

    // create device /sys/class/... entry
    if (device_create(dev_class, NULL, char_dev, NULL, CHAR_NAME) == NULL) {
        printk(KERN_ERR LOG "couldn't create device\n");
        unregister_chrdev_region(char_dev, 1);
        class_destroy(dev_class);
        return -1;
    }

    // /dev/... should be created automatically
    // if not use mknod
    printk(KERN_INFO LOG "driver loaded\n");

    // initialize get_sample() function pointer
    mode = 0;
    get_sample_ptr = &get_sample_res;

    return 0;
}

/**
 * destroys and unloads character device
 */
void __exit mod_exit(void) {
    // destroy and unload everything
    device_destroy(dev_class, char_dev);
    class_destroy(dev_class);
    cdev_del(&dev_cdev);
    unregister_chrdev_region(char_dev, 1);
    // if buffer is not empty, clear it
    if (bit_buffer != NULL) {
        kfree(bit_buffer);
        bit_buffer = NULL;
        printk(KERN_INFO LOG "free bit_buffer\n");
    }
    printk(KERN_INFO LOG "removed successfully\n");
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Niclas Kühnapfel");
MODULE_DESCRIPTION("Transceiver for bidirectional communication with LEDs and lasers");

module_init(mod_init);
module_exit(mod_exit);

