#!/usr/bin/env python3

from serial import Serial
from time import sleep
import argparse

# serial device (arduino)
ser = None


def initSerial(device):
    """
    Initialize serial connection and reset arduino
    :param device: device name (e.g. /dev/ttyACM0)
    :return: 0 if successful
    """
    global ser
    ser = Serial(device, baudrate=115200, xonxoff=0, rtscts=0)

    # reset arduino
    ser.setDTR(False)
    sleep(1)
    ser.flushInput()
    ser.setDTR(True)

    # start communication
    if ser.read() == b"\x00":
        print("Arduino is ready")
        sleep(2)
        return 0

    return -1


def selectMode(one, zero, guard):
    """
    Set bit durations
    :param one: duration of binary one
    :param zero: duration of binary zero
    :param guard: duration of delay between two bits
    :return: 0 if successful, -1 if not
    """
    ser.write((str(one) + "\n").encode("utf-8"))
    ser.write((str(zero) + "\n").encode("utf-8"))
    ser.write((str(guard) + "\n").encode("utf-8"))

    if ser.read() != b"\x00":
        print("Error in communication")
        return -1
    return 0


def sendData(data):
    """
    Move data to arduino for transmitting
    :param data: data to transmit
    :return: 0 if successful, -1 if not
    """
    # send length
    length = str(len(data)) + "\n"
    ser.write(length.encode("utf-8"))
    if ser.read() == b"\x01":
        print("No free space on arduino")
        return -1

    # send data
    ser.write(data)
    if ser.read() == b"\x00":
        return 0

    print("No ACK from arduino")
    return -1


def directTyping():
    """
    Transmit entered string
    :return: None
    """
    print("Type in message and press enter:")
    while True:
        data = input()
        if sendData(data.encode("utf-8")) == 0:
            print("ok")
        else:
            print("Error while sending data")


def sendFile(file):
    """
    Transmit file
    :param file: file to transmit
    :return: None
    """
    with open(file, "rb") as f:
        bytes = f.read()
        if sendData(bytes) == 0:
            print("Sent whole file")
        else:
            print("Error while sending file")


def measure(value):
    """
    Transmit test data for channel measurements
    :param value: 0 for 50*0x00, 1 for 50*0xff, None for 100*0xaa
    :return: None
    """
    if value == 0:
        data = bytes([0x00] * 50)
    elif value == 1:
        data = bytes([0xff] * 50)
    else:
        data = bytes([0xaa] * 100)
    if sendData(data) == 0:
        print("Sent test data")
    else:
        print("Error while sending test data")


def main():
    """
    Main: Parse arguments and do what the user wants
    :return: None
    """
    parser = argparse.ArgumentParser(description='Send data using arduino and laser')
    parser.add_argument('-d', '--device', help='serial port of arduino', required=True)
    time_group = parser.add_mutually_exclusive_group(required=True)
    time_group.add_argument('-m', '--mode', help='0 for Raspberry Pi, 1 for T21P, 2 for TL-WR1043ND, 3 for TL-MR3020')
    time_group.add_argument('-b', '--bits', nargs='+', type=int, help='ONE ZERO GUARD set bit durations in us')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--typing', help='direct typing', action='store_true')
    group.add_argument('-f', '--file', help='file to send')
    group.add_argument('--measure', type=int,
                       help='send only zeros (1), ones (2) or both (3) to measure their durations')
    args = parser.parse_args()

    if initSerial(args.device) == -1:
        print("An error occurred.")
        exit()

    if args.bits is not None:
        if selectMode(args.bits[0], args.bits[1], args.bits[2]) != 0:
            print("Error selecting mode")
    else:
        if args.mode == "0":
            if selectMode(150, 75, 40) != 0:
                print("Error selecting mode")
        elif args.mode == "1":
            if selectMode(7000, 3000, 3000) != 0:
                print("Error selecting mode")
        elif args.mode == "2":
            if selectMode(400, 200, 100) != 0:
                print("Error selecting mode")
        elif args.mode == "3":
            if selectMode(100, 100, 100) != 0:
                print("Error selecting mode")
        else:
            print("Mode not supported")

    if args.typing == True:
        directTyping()

    if args.file is not None:
        sendFile(args.file)

    if args.measure is not None:
        measure(args.measure)


if __name__ == "__main__":
    main()
