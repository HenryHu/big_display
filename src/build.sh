#!/bin/sh

mkdir -p /tmp/out

FILE=main.ino

ARGS="-prefs build.partitions=huge_app -prefs upload.maximum_size=3145728 -verbose -libraries $HOME/proj/arduino/libraries -hardware $HOME/proj/arduino/hardware -tools /usr/local/arduino/tools -tools /usr/bin -fqbn esp32:esp32:esp32 -build-path /tmp/out -build-cache $HOME/proj/arduino/cache $FILE"

arduino-builder -dump-prefs $ARGS
arduino-builder $ARGS

if [ $? -ne 0 ]; then
    exit 1
fi

esptool.py --chip esp32 --port /dev/cuaU1 --baud 921600 write_flash -z --flash_mode dio --flash_freq 80m --flash_size 4MB 0x10000 /tmp/out/$FILE.bin
