EXTRA_CFLAGS := -I$(PWD)/../../src -I$(PWD)
obj-m += led_transceiver.o

all:
	cp ../../src/led_transceiver.c ./
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules

clean:
	rm led_transceiver.c
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
