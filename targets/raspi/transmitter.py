import os, argparse, subprocess, ctypes
from fcntl import ioctl
from array import array
from ioctl_opt import IOR, IOW

# setting defines from kernel module
MAX_DUR = 0
CAP_LOAD = 1
CAP_UNLOAD = 2
GPIO = 3
BUF_LEN = 4
MODE_RES = 0
MODE_CAP = 1
GUARD = 5
BIT_DUR = 6
PREAMBLE = 7

# ioctl defines
STATUS = IOR(0x77, 0x00, ctypes.c_int)
MODE = IOW(0x77, 0x01, ctypes.c_int)
GET_SAMPLE = IOR(0x77, 0x02, ctypes.c_int)
RECEIVE = IOR(0x77, 0x03, ctypes.c_int)
SETTING = IOW(0x77, 0x04, ctypes.c_int)
MEASURE_LOAD = IOR(0x77, 0x05, ctypes.c_int)
TRANSMIT = IOR(0x77, 0x06, ctypes.c_int)
TRANSMIT_TEST = IOR(0x77, 0x07, ctypes.c_int)


class KMod:
    def __init__(self, name, gpio, debug=False):
        """
        Kernel module interface
        :param name: char device name
        :param gpio: pin number
        :param debug: print debug messages or not
        """
        self.dev = open(name, "wb")
        self.fd = self.dev.fileno()
        self.gpio = gpio
        self.setting(GPIO, gpio)
        self.debug = debug

    def dbg(self, text):
        """
        Print debug message
        :param text: message
        :return: None
        """
        if self.debug:
            print(text)

    def setting(self, name, value):
        """
        Set preference in kernel module via io call
        :param name: setting name
        :param value: setting value
        :return: None
        """
        ctl = array("i", [name, value])
        ioctl(self.fd, SETTING, ctl)

    def set_bit_dur(self, bit_dur):
        """
        Set duration of one bit
        :param bit_dur: time in us
        :return: None
        """
        self.dbg("set bit duration to: " + str(bit_dur))
        self.setting(BIT_DUR, bit_dur)

    def set_guard_dur(self, guard_dur):
        """
        Set duration of delay between two bits
        :param guard_dur: time in us
        :return: None
        """
        self.dbg("set guard duration to: " + str(guard_dur))
        self.setting(GUARD, guard_dur)

    def set_preamble(self, preamble):
        """
        Set flag if preamble should be sent or not
        :param preamble: Boolean
        :return: None
        """
        self.dbg("set preamble: " + str(preamble))
        self.setting(PREAMBLE, preamble)

    def start_transmission(self):
        """
        Start the actual transmission
        :return: None
        """
        ioctl(self.fd, STATUS)
        self.dbg("starting transmission")
        length = array("i", [0])
        ioctl(self.fd, TRANSMIT, length)
        self.dbg("transmitted bytes: " + str(length[0]))

    def write_data(self, data):
        """
        Write data to char device
        :param data: binary data
        :return: None
        """
        os.write(self.fd, data)

    def test_sequence(self):
        """
        Start transmission of test sequence
        :return: None
        """
        ioctl(self.fd, STATUS)
        self.dbg("starting transmission")
        length = array("i", [0])
        ioctl(self.fd, TRANSMIT_TEST, length)
        self.dbg("transmitted bytes: " + str(length[0]))


def main():
    parser = argparse.ArgumentParser(description="transmits data using LEDs")
    parser.add_argument("-f", "--file", help="read from file file")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug messages")
    parser.add_argument("-p", "--preamble", action="store_true", help="transmit preamble")
    parser.add_argument("-b", "--bit", type=int, help="bit duration")
    parser.add_argument("-g", "--guard", type=int, help="guard duration")
    parser.add_argument("--test_sequence", action="store_true", help="send test sequence")
    args = parser.parse_args()

    mod = KMod("/dev/led_transceiver", 26, debug=args.debug)

    if args.file:
        with open(args.file, 'rb') as f:
            data = f.read()
    elif args.test_sequence:
        pass
    else:
        print("Type in what you would like to send:")
        data = input().encode()

    mod.set_bit_dur(args.bit or 10)
    mod.set_guard_dur(args.guard or 0)
    if args.preamble:
        mod.set_preamble(1)
    else:
        mod.set_preamble(0)
    if args.test_sequence:
        mod.test_sequence()
    else:
        mod.write_data(data)
        mod.start_transmission()


if __name__ == "__main__":
    main()
