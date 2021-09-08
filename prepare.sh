#!/bin/bash

if [ "$1" = "raspi" ]; then
  echo "Please compile on the Raspberry Pi itself"
elif [ "$1" = "wr1043nd" ]; then
  cd targets/wr1043nd
  git clone https://github.com/openwrt/openwrt -b v18.06.9
  cd openwrt
  ./scripts/feeds update -a
  ./scripts/feeds install -a
  cp ../wr1043nd.config .config
  make defconfig
  make download
  patch < ../free_gpio.patch -p0
  make -j5
  cd ../../../
elif [ "$1" = "mr3020" ]; then
  cd targets/mr3020
  git clone https://github.com/openwrt/openwrt -b v18.06.9
  cd openwrt
  ./scripts/feeds update -a
  ./scripts/feeds install -a
  cp ../mr3020.config .config
  make defconfig
  make download
  patch < ../free_gpio.patch -p0
  make -j5
  cd ../../../
elif [ "$1" = "t21p" ]; then
  cd targets/t21p

  # build crosstool-ng
  git clone https://github.com/crosstool-ng/crosstool-ng
  cd crosstool-ng
  ./bootstrap
  ./configure --enable-local
  make
  cat ../ct-ng.config > .config
  ./ct-ng upgradeconfig
  ./ct-ng build
  cd ..

  # build kernel (headers needed for module)
  wget https://git.kernel.org/pub/scm/linux/kernel/git/rt/linux-stable-rt.git/snapshot/linux-stable-rt-3.4.20-rt31.tar.gz
  tar -zxvf linux-stable-rt-3.4.20-rt31.tar.gz
  rm linux-stable-rt-3.4.20-rt31.tar.gz
  # patch linux version
  echo "-rt31+" > linux-stable-rt-3.4.20-rt31/localversion-rt
  cd linux-stable-rt-3.4.20-rt31
  cat ../kernel.config > .config
  # patch old perl code
  sed -i 's/defined//g' kernel/timeconst.pl
  make ARCH=arm CROSS_COMPILE=../x-tools/arm-926ejs-linux-uclibcgnueabi/bin/arm-926ejs-linux-uclibcgnueabi-
  cd ../../../
else
  echo "Usage: ./prepare.sh [TARGET]"
fi
