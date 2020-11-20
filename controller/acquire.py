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

N = 100
captureIntervals = 6


def setupLogger():
    logFilePath = os.path.join(directory, "data/log_{}.log".format(recTimeStamp))
    logging.basicConfig(level=logging.INFO, 
                        handlers=[logging.FileHandler(logFilePath), 
                                  logging.StreamHandler()])
    def print(s):
        logging.info(s)


def connectToInternet():
    print("... Connecting.")
    # Activate 3G modem (turns off if it lost power)
    s = Serial("/dev/ttyUSB2", baudrate=115200)
    s.write("""AT#ECM=1,0,"","",0\r""".encode())
    s.close()
    
    # Simple HEAD request to test internet connection.
    conn = HTTPConnection("www.google.com", timeout=10)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return 1
    except:
        conn.close()
        return 0


def readData(ser, N):
    data = []
    while len(data) != N:
        line = ser.readline()
        line = line[0:len(line)-2].decode("utf-8", errors='replace')
        try:
            vector = [float(e) for e in line.split(',')]
            if len(vector) == 4:
                data.append(vector)
        except ValueError:
            continue
    return data


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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server, username=username)
    sftp = ssh.open_sftp()
    sftp.put(os.path.join(directory, filepath), os.path.join("C:/SnowOptics", filepath))
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    setupLogger()
    
    # ports = [e.device for e in list_ports.comports()]
    # print("Available ports: ", ports)
    
    r = connectToInternet()
    print("... Internet is {}.".format(["DOWN", "UP"][r]))
    
    print("... Acquiring.")
    data = []
    nanoPorts = ['/dev/ttyACM0']
    nanoPorts *= 4  # duplicate single COM x4 for testing
    for port in nanoPorts:
        s = Serial(port, baudrate=115200)
        s.flushInput()

        raw = np.asarray(readData(ser=s, N=N))
        data.append(raw)
        s.close()

    data = np.concatenate(data, axis=1)  # shape (N, 16)
    data = np.mean(data, axis=0)  # shape (16,)

    dataFilePath = "data/PD_{}.txt".format(recTimeStamp)
    np.savetxt(os.path.join(directory, dataFilePath), data)
    print("... Saved to disk.")

    copyToServer(dataFilePath)
    print("... Data saved to server.")
    
    if captureRequired(interval=captureIntervals):
        imageFilePath = "data/image_{}.jpg".format(recTimeStamp)
        capture(os.path.join(directory, imageFilePath))
        copyToServer(imageFilePath)
        print("... Image saved to server.")
    
    print("Acquisition successful. ")
    
    # os.system("shutdown now")
