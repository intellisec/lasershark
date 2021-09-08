# Scripts and Tools for the LaserShark Attack

Every tool except the kernel module prints out usage information via
`-h, --help`. if you have followed the [build instructions](build.md),
the tools mentioned below can be found in the `build\$target` directory.

Folder structure of the repository:

```
└─── targets
│   └─── $target
│   │   │   kernel config files
│   │   │   patches
│   │   │
│   │   └─── kernel_module
│   │   │   │   Makefile (compiles kernel module with specific cross compiler)
│   │   │
│   │   └─── tools   
│   │       │   Makefile (compiles receiver and transmitter app)
│   │       │   settings.h (settings for specific target)
│   │       │   target specific apps
│   │
│   └─── src
│       │   common.c (methods communicating with kernel module)
│       │   common.h (shared defines)
│       │   led_transceiver.c (transceiver kernel module)
│       │   receiver.c (receiver app for most of the targets)
│       │   transmitter.c (transmitter app for most of the targets)
│
└─── attacker
│   │   send.py (host tool)
│   │   laser.ino (Arduino modulation code)
│   │
│   └─── t21p
│       │   poc.py (root exploit)
│       │   upload.py (upload files)
│   
└─── stats
│   │   scripts for determining device statistics
│   
└─── pre_built
    │   pre-built images and tools
```

#### led_transceiver.ko 
Kernel module for all targets. Waits for the GPIO to become high the first time (20 seconds) and
measures how long the pin is in high state until it stays low for a specific amount of time (2 * max_duration).
It can also measure the time to load a capacitor that is connected with LED, GPIO and resistor. 
It is also able to transmit data by modulating a LED.
The module can be inserted ìnto a running kernel by:

```bash
sudo insmod led_transceiver.ko
```

Normally it creates its own `/dev/led_transceiver` entry. If not, use `mknod`:

```bash
cat /sys/devices/virtual/led_transceiver/led_transceiver/dev
mknod /dev/led_transceiver c $major $minor
```

#### settings.h
The configuration for the `receiver` and `transmitter` is stored in `settings.h`. They can only be
changed before compiling the `receiver` application.
 
```c
#ifndef SETTINGS_H
#define SETTINGS_H

// example (do not use)
#define GPIO_PIN 1
#define REC_MODE 0
#define BIT_BUFFER_LENGTH 8000
#define MIN_DUR 10
#define MAX_DUR 1000000
#define CAP_LOAD_TIME 1000
#define CAP_UNLOAD_TIME 20
#define DISABLE_AR9331_WD

#endif
```

- `GPIO_PIN`
    - GPIO pin connected to the receiving LED
- `REC_MODE`
    - set receiving mode
    - 0 if LED and resistor circuit
    - 1 if LED, resistor and capacitor circuit
- `BIT_BUFFER_LENGTH`
    - number of bits that can be stored in the kernel module
- `MIN_DUR`
    - minimal duration to be considered as real bit
    - there may be some bad measurements which will be removed if their duration is smaller than this value
- `MAX_DUR`
    - maximum duration to be considered as real bit
- `CAP_LOAD_TIME`
    - time in microseconds that is needed to load the capacitor
- `CAP_UNLOAD_TIME`
    - time in microseconds that is needed to unload the capacitor
- `DISABLE_AR9331_WD`
    - if this define is set, the receiver tries to disable the hardware watchdog on ar9331

#### receiver

Receiver application for all targets except the Raspberry Pi. Takes measured bit durations from kernel module, 
demodulates data and prints or saves it. Also able to do measurements.

```bash
Usage: ./receiver (-m | -d | -l | -f FILE) CENTER

arguments:                                       
 -m measurement                                  
 -d write data to stdout                         
 -f FILE write data to file                      
 -l measure capacitor load time                  
 CENTER time to decide between 0 and 1
```

- `-m`   
    - measures duration of received bits 
    - shows average, minimum and maximum as output
    - can be used to determine CENTER value if only ones or zeros are sent
- `-l`
    - measures how long it takes to load the capacitor
    - can be used to determine the cap_load time value for settings
- `CENTER`  
    - this value is used to decide whether a measured duration is a one or a zero
    - internally also used to detect the end of a transmission (if 3 * center no bit detected -> end of transmission)
    - unit: microseconds
    
#### transmitter
Transmitter application for all targets except the Raspberry Pi. Takes bit durations to modulate a LED.

```bash
Usage: ./transmitter -p -g GUARD -b BIT_DUR -o PIN -f FILE

arguments:                                              
 -p activates preamble                                  
 -g GUARD guard time                                    
 -b BIT bit time                                        
 -o PIN GPIO pin                                        
 -f FILE data to send 
```

- `-p`
    - activates preamble
- `-g`
    - guard time between bits in us
- `-o`
    - specifies GPIO pin
- `-f` 
    - transmit this file
    
#### receiver.py

Receiver application for the Raspberry Pi. No external settings file needed as there are extended command line options.

```bash
usage: receiver.py [-h] [-f FILE] [-d] [-m] [-l LOAD] [-u UNLOAD]
                   [--upper_limit UPPER_LIMIT] [--lower_limit LOWER_LIMIT]
                   [--measure_load]
                   MODE CENTER

receives data using LED receiver kernel module

positional arguments:
  MODE                  'res' or 'cap' mode
  CENTER                value to determine if zero or one was sent (also
                        needed to decide wether a transmission is over or not)

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  write to file
  -d, --debug           enable debug messages
  -m, --measure         start measurement
  -l LOAD, --load LOAD  time to load the capacitor
  -u UNLOAD, --unload UNLOAD
                        time to unload the capacitor
  --upper_limit UPPER_LIMIT
                        limit for bit duration
  --lower_limit LOWER_LIMIT
                        limit for bit duration
  --measure_load        measure time to load the capacitor
```

Please check `receiver` and `settings.h` documentation for more information on these options.

#### transmitter.py
Transmitter application for the Raspberry Pi. No external settings file needed as there are extended command line options.

```bash
usage: transmitter.py [-h] [-f FILE] [-d] [-p] [-b BIT] [-g GUARD] [--test_sequence]

transmits data using LEDs

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  read from file file
  -d, --debug           enable debug messages
  -p, --preamble        transmit preamble
  -b BIT, --bit BIT     bit duration
  -g GUARD, --guard GUARD
                        guard duration
  --test_sequence       send test sequence
```

Please check `transmitter` and `settings.h` documentation for more information on these options.

#### send.py

Sends data via Arduino and laser. Arduino must be connected to host and the `laser.ino` sketch must be running. 
The Arduino takes care of modulation.

```bash
usage: send.py [-h] -d DEVICE (-m MODE | -b BITS [BITS ...])
               (-t | -f FILE | --measure MEASURE)

Send data using Arduino and laser

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        serial port of Arduino
  -m MODE, --mode MODE  0 for Raspberry Pi, 1 for T21P, 2 for TL-WR1043ND, 3
                        for TL-MR3020
  -b BITS [BITS ...], --bits BITS [BITS ...]
                        ONE ZERO GUARD set bit durations manual
  -t, --typing          direct typing
  -f FILE, --file FILE  file to send
  --measure MEASURE     send only zeros (1), ones (2) or both (3) to measure
                        their durations
```

- `-d DEVICE`
    - the Arduino itself
    - for example /dev/ttyACM0
- `-m MODE`
    - 0 for LED and resistor circuit
    - 1 for LED, capacitor and resistor circuit
- `-b ONE ZERO GUARD`
    - set bit durations manually
    - ONE duration of one
    - ZERO duration of zero
    - GUARD guard time
- `--measure MEASURE` 
    - send 800 bits 
    - can be used easily with measure options on the receiver side
    - MEASURE = 0 -> 400 * 0
    - MEASURE = 1 -> 400 * 1
    - MEASURE = 2 -> 200 * 1 + 200 * 0

#### Important for high speed transmissions

The Arduino may be too slow to get the durations from variables. If you
want to try higher bitrates than the ones in the examples, try to hardcode
the timing variables.