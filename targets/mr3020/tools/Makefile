CROSS_COMPILE := $(PWD)/../openwrt/staging_dir/toolchain-mips_24kc_gcc-*/bin/mips-openwrt-linux-

all: receiver transmitter

receiver: receiver.o common.o
	$(CROSS_COMPILE)gcc -o receiver receiver.o common.o

transmitter: transmitter.o common.o
	$(CROSS_COMPILE)gcc -o transmitter transmitter.o common.o

receiver.o: ../../src/receiver.c ../../src/common.h settings.h
	$(CROSS_COMPILE)gcc -c ../../src/receiver.c -I$(PWD)

transmitter.o: ../../src/transmitter.c ../../src/common.h settings.h
	$(CROSS_COMPILE)gcc -c ../../src/transmitter.c -I$(PWD)

common.o: ../../src/common.c ../../src/common.h
	$(CROSS_COMPILE)gcc -c ../../src/common.c -std=gnu99

clean:
	rm receiver transmitter *.o
