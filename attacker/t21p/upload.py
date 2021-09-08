import telnetlib
import tftpy
import threading
import argparse

tftp = None
tn = None


def tn_send(msg):
    """
    Send telnet command
    :param msg: command
    :return: stdout of command
    """
    tn.write(msg.encode("utf-8"))
    return tn.read_until("#".encode("utf-8")).decode("utf-8")


def tn_start_tools(telephone, server):
    """
    Execute commands on t21p: upload files and prepare kernel module
    :param telephone: IP address of t21p
    :param server: IP of host (ftp server)
    :return: None
    """
    global tn
    tn = telnetlib.Telnet(telephone)
    tn.read_until("#".encode("utf-8"))
    tn_send("cd /var/tmp\n")
    tn_send("rm /dev/led_transceiver\n")
    tn_send("rmmod led_transceiver.ko\n")
    tn_send("rm led_transceiver.ko\n")
    tn_send("rm receiver\n")
    tn_send("rm transmitter\n")
    tn_send("rm data\n")
    tn_send("tftp -r led_transceiver.ko -l led_transceiver.ko -g " + server + " 1234\n")
    tn_send("tftp -r receiver -l receiver -g " + server + " 1234\n")
    tn_send("tftp -r transmitter -l transmitter -g " + server + " 1234\n")
    tn_send("tftp -r data -l data -g " + server + " 1234\n")
    tn_send("insmod led_transceiver.ko\n")
    tn_send("chmod +x receiver\n")
    tn_send("chmod +x transmitter\n")
    text = tn_send("cat /sys/devices/virtual/led_transceiver/led_transceiver/dev\n").split("\r\n")
    major = text[1].split(":")[0]
    minor = text[1].split(":")[1]
    print("major: " + major + " minor: " + minor)
    tn_send("mknod /dev/led_transceiver c " + major + " " + minor + "\n")
    text = tn_send("cat /sys/devices/virtual/led_transceiver/led_transceiver/dev\n").split("\r\n")
    major = text[1].split(":")[0]
    minor = text[1].split(":")[1]
    print("major: " + major + " minor: " + minor)
    tn_send("mknod /dev/led_transceiver c " + major + " " + minor + "\n")


def start_tftp(path):
    """
    Start ftp server
    :param path: ftp root path
    :return: None
    """
    global tftp
    tftp = tftpy.TftpServer(path)
    tftp.listen('0.0.0.0', 1234)


def main():
    """
    Main: Upload necessary files and insert kernel module
    :return: None
    """
    parser = argparse.ArgumentParser(description="Uploads receiver and kernel module to telephone")
    parser.add_argument('-t', '--telephone', help='IP of telephone', required=True)
    parser.add_argument('-i', '--ip', help='IP of host', required=True)
    parser.add_argument('-f', '--folder', help='folder with receiver and kernel module')
    args = parser.parse_args()

    folder = args.folder or "../build/t21p/"

    # start tftp server
    tftp_thread = threading.Thread(target=start_tftp, args=(folder,))
    tftp_thread.start()
    print("tftp server is running")

    # start tools on telephone
    tn_start_tools(args.telephone, args.ip)
    print("receiver and kernel module uploaded")

    # stop everything
    tftp.stop()
    tftp_thread.join()
    print("tftp server stopped")


if __name__ == '__main__':
    main()
