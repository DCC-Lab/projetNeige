"""
!!!!!! NEVER MODIFY THIS FILE !!!!!!
This script is launched first as a standalone to initialize 3G internet
 connection and open reverse SSH. Only after that, acquisition script is executed.

Modifying this file in the running Pi could accidentally corrupt it
 which would then disable the device's connection to the server
 or any remote backdoor forever (requiring local access).

For added security, remove write-permission locally.
"""

import os
import time
import logging
import subprocess
from serial import Serial
from datetime import datetime
from http.client import HTTPConnection

# Controller directory
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Log file
recTimeStamp = datetime.now().strftime("%y%m%d_%H%M")
logFilePath = "data/logConnectPrimary_{}.log".format(recTimeStamp)
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(os.path.join(directory, logFilePath)),
                              logging.StreamHandler()])
logging.getLogger("paramiko").setLevel(logging.WARNING)


def connectToInternet(tries=2):
    try:
        logging.info(".Connect.")
        # Activate 3G modem (it is deactivated when it loses power)
        s = Serial("/dev/ttyUSB2", baudrate=115200, timeout=10)
        s.write("""AT#ECM=1,0,"","",0\r""".encode())
        s.close()

        # Tiny HEAD request to test internet connection.
        conn = HTTPConnection("www.google.com", timeout=10)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return 1
        except Exception as e:
            logging.info("E.HTTP: {}".format(type(e).__name__))
            conn.close()
            if tries > 1:
                time.sleep(2)
                return connectToInternet(tries=tries-1)
            return 0
    except Exception as e:
        logging.info("E.3G: {}".format(type(e).__name__))
        return 0


if __name__ == '__main__':
    time.sleep(2)
    timeCon = time.time()
    r = connectToInternet(tries=2)
    while r == 0 and time.time() - timeCon < 20:
        time.sleep(1)
        r = connectToInternet(tries=1)

    logging.info("Web {}".format(["DOWN", "UP"][r]))
    if r == 1:
        subprocess.Popen('ssh -N -R 2222:localhost:22 Alegria@24.201.18.112', shell=True, close_fds=True)
        logging.info("RSSH Open")
    logging.info("ConTime={}s".format(time.time() - timeCon))
    time.sleep(5)

    # Launch acquisition script (Not imported to avoid compile errors)
    acquireFilePath = os.path.join(directory, "local/acquirePrimary.py")
    os.system("python3 {}".format(acquireFilePath))
