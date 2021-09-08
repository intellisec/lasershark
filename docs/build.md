# Building Device Images

With the following instructions you can build everything that is
necessary to deploy and make use of the LaserShark attack for different
target devices.

This requires a specialized hardware setup. If you do not have such at
hand you of course can still build the images, but won't be able to put
the attack in practice. However, to still toy around with the
implementations, we have prepared
[quickstart instructions](docs/quickstart.md) to get you started with a
simple example.

## Dependencies

We assume a Ubuntu 21.04 system and provide the dependencies as commands
as they would be used for installing them:

```bash
sudo apt install \
	autoconf \
	bison \
	build-essential \
	ecj \
	g++ \
	gawk \
	gcc \
	gettext \
	fastjar \
	flex \
	file \
	git \
	help2man \
	java-propose-classpath \
	libelf-dev \
	libncurses-dev \
	libncurses5-dev \
	libssl-dev \
	libtool-bin \
	make \
	python \
	python3-dev \
	python3-distutils \
	python3-pip \
	subversion \
	texinfo \
	time \
	unzip \
	wget \
	zlib1g-dev

sudo pip3 install ioctl-opt
```

If you use a Raspberry Pi in the process (as a target or controller)
please update the Raspberry Pi OS (formerly Raspbian) kernel and install
additional dependencies:

```bash
sudo apt update
sudo apt upgrade
sudo rpi-update
sudo apt install raspberrypi-kernel-headers wiringpi
```

## Targets
Our implementations have been tested against the following targets:

#### Raspberry Pi Model 3B+ (raspi)
- CPU: BCM2837B0 (arm64)
- GPIO: 26 (on pin header)
- root access: SSH

#### Yealink T21P-E2 (t21p)
- CPU: DSPG DVF-9918 (arm926ej-s)
- GPIO: 112 (green LED under button, LED1)
- root access: CVE-2018-16217 (poc.py)

#### TP-Link TL-WR1043ND v1 (wr1043nd)
- CPU: Atheros AR-9132 (mips_24kc)
- GPIO: Pin 5 (QSS-Led D31)
- root access: SSH (OpenWrt image)

#### TP-Link TL-MR3020 v1.x (mr3020)
- CPU: Atheros AR-9331 (mips_24kc)
- GPIO: Pin 0 (WiFi-LED LED4)
- root access: SSH (OpenWrt image)


## Building the Toolchain
To download and build a cross-compiler run: 

```bash
./prepare.sh [TARGET]
```

This will also generate images for the TP-Link devices
(`targets/$target/openwrt/bin/targets/ar71xx/`) needed  to access
to the GPIO pins. 

As `[TARGET]` you can choose any folder name under `targets/`, e.g.,
`t21p`, `mr3020`, or `wr1043nd`. There, however, is no cross-compiler
for the Raspberry Pi, but you can build everything directly on the RPi
itself.


#### Compile
To compile a kernel module, receiver and transmitter run:

```bash
./build.sh [TARGET]
```

Builds are copied to the `build/` directory. Building the source for the Raspberry Pi will only work on Raspberry Pi.

#### Cleanup
To remove a build run:

```bash
./clean.sh [TARGET] build
```

To remove a specific toolchain run:

```bash
./clean.sh [TARGET] toolchain
```

## Usage

Please refer to the [usage instructions](usage.md) for details on the
how to use the provided scripts. **Note,** that these requires you to
have built and deployed the images/toolchains at the respective hardware
devices. If you do not have any hardware at hand you won't be able to
tests these scripts :(
