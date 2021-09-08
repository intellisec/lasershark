KERNEL_DIR := ../linux-stable-rt-3.4.20-rt31
ARCH := arm
CROSS_COMPILE := ../x-tools/arm-926ejs-linux-uclibcgnueabi/bin/arm-926ejs-linux-uclibcgnueabi-

EXTRA_CFLAGS := -I$(PWD)/../../src -I$(PWD)
obj-m += led_transceiver.o

all:
	cp ../../src/led_transceiver.c ./
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	rm led_transceiver.c
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(PWD) -C $(KERNEL_DIR) clean
