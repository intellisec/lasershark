KERNEL_DIR := $(PWD)/../openwrt/build_dir/target-mips_24kc_musl/linux-ar71xx_generic/linux-*
ARCH := mips
CROSS_COMPILE := $(PWD)/../openwrt/staging_dir/toolchain-mips_24kc_gcc-*/bin/mips-openwrt-linux-

EXTRA_CFLAGS := -I$(PWD)/../../src -I$(PWD)
obj-m += led_transceiver.o

all:
	cp ../../src/led_transceiver.c ./
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	rm led_transceiver.c
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(PWD) -C $(KERNEL_DIR) clean
