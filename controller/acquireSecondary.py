import os
import sys
import time
import logging
import paramiko
import numpy as np
from serial import Serial
from datetime import datetime
from picamera import PiCamera
from serial.tools import list_ports
from http.client import HTTPConnection
import traceback

time0 = time.time()
directory = os.path.dirname(os.path.abspath(__file__))
recTimeStamp = datetime.now().strftime("%y%m%d_%H%M")

"""
RaspBerry Pi Acquisition Script
Launched at startup

- Check for Git updates (?)
- Activate 3G modem
- Wait for internet connection
- For each COM, integrate signal for N points. Each COM corresponds to 4 PD.
- Save data to file
- Take picture if it's time to (interval check)
- Send data and image to server over SSH
"""

N = 20
captureIntervals = 6


logFilePath = "data/log_{}.log".format(recTimeStamp)
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(os.path.join(directory, logFilePath)),
                              logging.StreamHandler()])


def print(s):
    logging.info(s)


def connectToInternet(tries=2):
    try:
        print("... Connecting.")

        # Simple HEAD request to test internet connection.
        conn = HTTPConnection("www.google.com", timeout=10)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return 1
        except Exception as e:
            print("Error with HTTP Request: {}".format(e))
            conn.close()
            if tries > 1:
                time.sleep(2)
                return connectToInternet(tries=tries-1)
            return 0
    except Exception as e:
        print("Error with 3G modem port: {}".format(e))
        return 0


def readData(ser, N) -> (int, list):
    try:
        nanoID = None
        localData = []
        while len(localData) != N:
            line = ser.readline()
            line = line[0:len(line)-2].decode("utf-8", errors='replace')
            try:
                vector = [float(e) for e in line.split(',')]
                if len(vector) == 5:
                    nanoID = int(vector[0])
                    localData.append(vector[1:])
            except ValueError:
                continue
        return nanoID, np.asarray(localData)
    except Exception as e:
        logging.info("Error reading data")


def captureRequired(interval: int = 6):
    countPath = os.path.join(directory, "data/count.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    if count % interval == 0:
        return True
    return False


def capture(filepath):
    camera = PiCamera()
    camera.capture(filepath)


# public 24.201.18.112, lan 192.168.0.188 
def copyToServer(filepath, server="24.201.18.112", username="Alegria"):
    # logging.info("SERVER SKIP!")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("/home", "pi", ".ssh", "known_hosts")))
        ssh.connect(server, username=username)
        sftp = ssh.open_sftp()
        sftp.put(os.path.join(directory, filepath), os.path.join("C:/SnowOptics", filepath))
        sftp.close()
        ssh.close()
    except Exception as e:
        logging.info("Cannot connect to server for {} : {}".format(filepath, type(e).__name__))
        logging.info(traceback.format_exc())

if __name__ == "__main__":
    time.sleep(5)

    ports = [e.device for e in list_ports.comports() if "USB" in e.device]
    print("Available ports: {}".format(ports))

    timeCon = time.time()
    r = connectToInternet(tries=2)
    while r == 0 and time.time() - timeCon < 10:
        time.sleep(1)
        r = connectToInternet(tries=2)

    print("... Internet is {}.".format(["DOWN", "UP"][r]))
    logging.info("Connection time of {}s".format(time.time() - timeCon))
    
    print("... Acquiring.")
    time.sleep(2)
    timeAcq = time.time()
    data = np.full(4*8, np.NaN)
    for port in ports:
        try:
            s = Serial(port, baudrate=115200, timeout=5)
            s.flushInput()
            print("... Port {}".format(port))
            nanoId, raw = readData(ser=s, N=N)  # (N, 4)
            raw = np.mean(raw, axis=0)  # (4,)
            fillIdx = (nanoId - 1) * 4
            data[fillIdx: fillIdx+4] = raw

            s.close()
        except Exception as e:
            logging.info("Error with port {} : {}".format(port, e))
            continue
        time.sleep(1)

    dataFilePath = "data/PD_{}.txt".format(recTimeStamp)
    np.savetxt(os.path.join(directory, dataFilePath), data)

    logging.info("Acquistion time of {}s, data shape {}".format(time.time() - timeAcq, data.shape))

    print("... Saved to disk.")

    copyToServer(dataFilePath)
    print("... Data saved to server.")
    
    if captureRequired(interval=captureIntervals):
        try:
            imageFilePath = "data/image_{}.jpg".format(recTimeStamp)
            capture(os.path.join(directory, imageFilePath))
            copyToServer(imageFilePath)
            print("... Image saved to server.")
        except Exception as e:
            logging.info("Camera is not available!")
    
    print("Acquisition successful. ")

    logging.info("Total elapsed time = {}s".format(time.time() - time0))

    copyToServer(logFilePath)

    # os.system("shutdown now")

