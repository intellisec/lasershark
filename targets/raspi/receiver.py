import os, argparse, subprocess, ctypes
from fcntl import ioctl
from array import array
from struct import unpack
from ioctl_opt import IOR, IOW

# setting defines from kernel module
MAX_DUR = 0
CAP_LOAD = 1
CAP_UNLOAD = 2
GPIO = 3
BUF_LEN = 4
MODE_RES = 0
MODE_CAP = 1

# ioctl defines
STATUS = IOR(0x77, 0x00, ctypes.c_int)
MODE = IOW(0x77, 0x01, ctypes.c_int)
GET_SAMPLE = IOR(0x77, 0x02, ctypes.c_int)
RECEIVE = IOR(0x77, 0x03, ctypes.c_int)
SETTING = IOW(0x77, 0x04, ctypes.c_int)
MEASURE_LOAD = IOR(0x77, 0x05, ctypes.c_int)


class KMod:
    def __init__(self, name, gpio, center, lower_limit, upper_limit, debug=False):
        """
        Kernel module interface
        :param name: char device name
        :param gpio: pin number
        :param center: decision threshold
        :param lower_limit: capacitor load time limit
        :param upper_limit: capacitor load time limit
        :param debug: print debug messages or not
        """
        self.dev = open(name, "rb")
        self.fd = self.dev.fileno()
        self.gpio = gpio
        self.setting(GPIO, gpio)
        self.debug = debug
        self.center = center
        self.lower_limit = lower_limit or 0
        self.upper_limit = upper_limit or 10000000

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

    def set_mode(self, mode):
        """
        Set mode of kernel module
        :param mode: res or cap
        :return: None
        """
        self.dbg("set mode to: " + str(mode))
        ctl = array("i", [mode])
        ioctl(self.fd, MODE, ctl)

    def set_cap(self, load, unload, max_duration):
        """
        Set capacitor mode
        :param load: duration to charge capacitor
        :param unload: duration to discharge capacitor
        :param max_duration: maximum delay between two bits
        :return: None
        """
        self.dbg("set capacitor mode")
        subprocess.run(["gpio", "-g", "mode", "26", "in"])
        subprocess.run(["gpio", "-g", "mode", "26", "tri"])
        self.setting(CAP_LOAD, load)
        self.setting(CAP_UNLOAD, unload)
        self.setting(MAX_DUR, max_duration)
        self.set_mode(MODE_CAP)

    def set_res(self, max_duration):
        """
        Set resistor mode
        :param max_duration: maximum delay between two bits
        :return: None
        """
        self.dbg("set resistor mode")
        subprocess.run(["gpio", "-g", "mode", "26", "in"])
        subprocess.run(["gpio", "-g", "mode", "26", "down"])
        self.setting(MAX_DUR, max_duration)
        self.set_mode(MODE_RES)

    def start_reception(self):
        """
        Start receive procedure
        :return: None
        """
        ioctl(self.fd, STATUS)
        self.dbg("starting reception")
        length = array("i", [0])
        ioctl(self.fd, RECEIVE, length)
        self.dbg("lenght: " + str(length[0]))
        return length[0]

    def measure(self, length):
        """
        Measure duration of received bits
        :param length: number of bits to receive
        :return: None
        """
        durations = []
        for x in range(length):
            line = self.dev.read(8)
            if len(line) == 8:
                i = unpack("q", line)[0]
                self.dbg(str(i))
                if self.lower_limit < i < self.upper_limit:
                    durations.append(i)
        if len(durations) > 0:
            print("min: " + str(min(durations)))
            print("max: " + str(max(durations)))
            print("center: " + str(sum(durations) / len(durations)))
        print("length: " + str(len(durations)))

    def measure_load(self):
        """
        Measure capacitor charge duration
        :return: None
        """
        self.dbg("measure capacitor load time")
        durations = []
        for x in range(50):
            load_time = array("i", [0])
            ioctl(self.fd, MEASURE_LOAD, load_time)
            durations.append(load_time[0])
        print("min: " + str(min(durations)))
        print("max: " + str(max(durations)))
        print("center: " + str(sum(durations) / len(durations)))
        print("length: " + str(len(durations)))

    def receive_chunk(self, length):
        """
        Receive data
        :param length: number of bits to read from kernel module
        :return: data
        """
        if length == 1:
            print("timeout")
        bytes = bytearray()
        bit_string = ""
        bit_counter = 0
        for x in range(length):
            line = self.dev.read(8)
            if len(line) == 8:
                i = unpack("q", line)[0]
                if self.lower_limit < i < self.center:
                    self.dbg(str(i))
                    bit_counter += 1
                    bit_string = bit_string + "0"
                if self.upper_limit > i > self.center:
                    self.dbg(str(i))
                    bit_counter += 1
                    bit_string = bit_string + "1"
            if bit_counter == 8:
                self.dbg(str(bit_string))
                x = int(bit_string, 2)
                bytes.append(x)
                bit_counter = 0
                bit_string = ""
        return bytes

    def direct_out(self, length):
        """
        Print received data in command line
        :param length: number of received bits
        :return: None
        """
        bytes = self.receive_chunk(length)
        data = ""
        for x in bytes:
            data += chr(x)
        print(data)

    def file_out(self, length, file_name):
        """
        Save received data to file
        :param length: number of received bits
        :param file_name: output file
        :return: None
        """
        bytes = self.receive_chunk(length)
        with open(file_name, "wb") as f:
            f.write(bytes)
        print("wrote to file")


def main():
    parser = argparse.ArgumentParser(description="receives data using LED receiver kernel module")
    parser.add_argument("-f", "--file", help="write to file")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug messages")
    parser.add_argument("-m", "--measure", action="store_true", help="start measurement")
    parser.add_argument("-l", "--load", type=int, help="time to load the capacitor")
    parser.add_argument("-u", "--unload", type=int, help="time to unload the capacitor")
    parser.add_argument("--upper_limit", type=int, help="limit for bit duration")
    parser.add_argument("--lower_limit", type=int, help="limit for bit duration")
    parser.add_argument("--measure_load", action="store_true", help="measure time to load the capacitor")
    parser.add_argument("MODE", help="'res' or 'cap' mode")
    parser.add_argument("CENTER", type=int, help="value to determine if zero or one was sent (also needed to decide "
                                                 "whether a transmission is over or not)")
    args = parser.parse_args()

    if args.MODE == "cap" and (args.load is None or args.unload is None):
        parser.error("cap mode requires --load and --unload")

    mod = KMod("/dev/led_transceiver", 26, args.CENTER, args.lower_limit, args.upper_limit, debug=args.debug)

    if args.MODE == "res":
        mod.set_res(args.CENTER * 2)
    elif args.MODE == "cap":
        mod.set_cap(args.load, args.unload, args.CENTER * 2)
    else:
        parser.error("mode not supported")

    if args.measure_load:
        mod.measure_load()
        return

    print("waiting for data")
    length = mod.start_reception()

    if args.measure:
        mod.measure(length)
    elif args.file:
        mod.file_out(length, args.file)
    else:
        mod.direct_out(length)


if __name__ == "__main__":
    main()
