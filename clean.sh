#!/bin/bash

if [ "$1" = "raspi" ]; then
  rm -rf build/raspi/
elif [ "$1" = "wr1043nd" ] && [ "$2" = "toolchain" ]; then
  rm -rf targets/wr1043nd/openwrt/
elif [ "$1" = "wr1043nd" ] && [ "$2" = "build" ]; then
  rm -rf build/wr1043nd/
elif [ "$1" = "mr3020" ] && [ "$2" = "toolchain" ]; then
  rm -rf targets/mr3020/openwrt/
elif [ "$1" = "mr3020" ] && [ "$2" = "build" ]; then
  rm -rf build/mr3020/
elif [ "$1" = "t21p" ] && [ "$2" = "toolchain" ]; then
  rm -rf targets/t21p/crosstool-ng
  rm -rf targets/t21p/build
  rm -rf targets/t21p/x-tools
  rm -rf targets/t21p/linux-stable-rt-3.4.20-rt31
elif [ "$1" = "t21p" ] && [ "$2" = "build" ]; then
  rm -rf build/t21p/
else
  echo "Usage: ./clean.sh [TARGET] [build | toolchain]"
fi