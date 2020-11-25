import os
import time
import logging
import paramiko
import subprocess
from serial import Serial
from shutil import copyfile
from datetime import datetime
from picamera import PiCamera
from serial.tools import list_ports
from http.client import HTTPConnection

time0 = time.time()
directory = os.path.dirname(os.path.abspath(__file__))
recTimeStamp = datetime.now().strftime("%y%m%d_%H%M")

"""
RaspBerry Pi Main Acquisition Script
Launched at startup

- Check for Git updates (?)
- Activate 3G modem
- Wait for internet connection
- Wait for Secondary Pi's data
- Take picture if it's time to (interval check)
- Send data, image and logs to server over SSH
- Auto shutdown if no backdoor enabled
"""

captureIntervals = 6


logFilePath = "data/logMain_{}.log".format(recTimeStamp)
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(os.path.join(directory, logFilePath)),
                              logging.StreamHandler()])


def print(s):
    logging.info(s)


def connectToInternet(tries=2):
    try:
        print("... Connecting.")
        # Activate 3G modem (turns off if it lost power)
        s = Serial("/dev/ttyUSB2", baudrate=115200, timeout=10)
        s.write("""AT#ECM=1,0,"","",0\r""".encode())
        s.close()

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


def getLaunchCount():
    countPath = os.path.join(directory, "data/count.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    return count


def backdoorState():
    filePath = os.path.join(directory, "data/backdoor.txt")
    with open(filePath, "r") as f:
        state = int(f.readlines()[0])
    return state


def capture(filepath):
    camera = PiCamera()
    camera.capture(filepath)


# public 24.201.18.112, lan 192.168.0.188 
def copyToServer(filepath, server="24.201.18.112", username="Alegria"):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(server, username=username)
        sftp = ssh.open_sftp()
        sftp.put(os.path.join(directory, filepath), os.path.join("C:/SnowOptics", filepath))
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logging.info("Cannot connect to server for {} : {}".format(filepath, type(e).__name__))
        return False


if __name__ == "__main__":
    time.sleep(5)
    autoShutdown = False

    ports = [e.device for e in list_ports.comports()]
    print("Available ports: {}".format(ports))

    timeCon = time.time()
    r = connectToInternet(tries=2)
    while r == 0 and time.time() - timeCon < 20:
        time.sleep(1)
        r = connectToInternet(tries=1)

    print("... Internet is {}.".format(["DOWN", "UP"][r]))
    if r == 1:
        subprocess.Popen('ssh -N -R 2222:localhost:22 Alegria@24.201.18.112', shell=True, close_fds=True)
        logging.info("Reverse Shell is Open")
    logging.info("Connection time of {}s".format(time.time() - timeCon))
    time.sleep(2)

    print("... Waiting for SecondaryPi's data.")

    timeAcq = time.time()
    acqTimeOut = 60
    fileDiff = []
    with open(os.path.join(directory, "data/fileHistory.txt"), "r") as f:
        pastFiles = [l.replace("\n", "") for l in f.readlines()]

    deltaAcq = 0
    while len(fileDiff) == 0 and deltaAcq < acqTimeOut:
        currentFiles = list(os.walk(os.path.join(directory, "dataSecondary")))[0][2]
        fileDiff = [f for f in currentFiles if f not in pastFiles]
        time.sleep(1)
        deltaAcq += 1

    if len(fileDiff) == 0:
        print("TIMEOUT ERROR for SecondaryPi's data")
    else:
        print("Received SecondaryPi's data in {}s".format(str(deltaAcq)))
        if len(fileDiff) == 1:
            time.sleep(6)
            currentFiles = list(os.walk(os.path.join(directory, "dataSecondary")))[0][2]
            fileDiff = [f for f in currentFiles if f not in pastFiles]
        for fileName in fileDiff:
            sourcePath = os.path.join(directory, "dataSecondary/{}".format(fileName))
            copyfile(src=os.path.join(directory, "dataSecondary/{}".format(fileName)),
                     dst=os.path.join(directory, "data/{}".format(fileName)))
            if not copyToServer("data/{}".format(fileName)):
                fileDiff.remove(fileName)
        with open(os.path.join(directory, "data/fileHistory.txt"), "w+") as f:
            f.write('\n'.join(currentFiles) + '\n')
        print("Data files ({}) sent to server".format(len(fileDiff)))
        autoShutdown = True

    logging.info("Acquistion time of {}s".format(time.time() - timeAcq))

    launchCount = getLaunchCount()
    if launchCount % captureIntervals == 0:
        try:
            imageFilePath = "data/image_{}.jpg".format(recTimeStamp)
            capture(os.path.join(directory, imageFilePath))
            copyToServer(imageFilePath)
            print("... Image sent to server.")
        except Exception as e:
            logging.info("Camera is not available!")

    if backdoorState() == 1:
        logging.info("Backdoor enabled")
        autoShutdown = False

    logging.info("Total elapsed time = {}s".format(time.time() - time0))
    if autoShutdown:
        logging.info("Shutting down")
    else:
        logging.info("Not shutting down")

    copyToServer(logFilePath)

    if autoShutdown:
        os.system("sudo shutdown now")
