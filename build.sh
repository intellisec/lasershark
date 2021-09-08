#!/bin/bash

target="ready"

if [ "$1" = "raspi" ]; then
  echo "Please compile on the Raspberry Pi itself"
  rm -R build/raspi
  mkdir -p build/raspi
  cd targets/raspi/kernel_module
  make
  cp led_transceiver.ko ../../../build/raspi
  make clean
  cd ..
  cp receiver.py ../../build/raspi
  cp transmitter.py ../../build/raspi
  cd ../../
elif [ "$1" = "wr1043nd" ]; then
  target="wr1043nd"
elif [ "$1" = "mr3020" ]; then
  target="mr3020"
elif [ "$1" = "t21p" ]; then
  target="t21p"
else
  target="null"
fi

if [ $target = "null" ]; then
  echo "Usage: ./build.sh [TARGET]"
elif [ $target = "ready" ]; then
  echo ""
else
  export STAGING_DIR=$(pwd)/$target/openwrt/staging_dir/
  rm -R build/$target
  mkdir -p build/$target
  cd targets/$target/kernel_module
  make
  cp led_transceiver.ko ../../../build/$target
  make clean
  cd ../tools
  make
  cp receiver ../../../build/$target
  cp transmitter ../../../build/$target
  make clean
  cd ../../../
fi
