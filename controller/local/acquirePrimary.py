import os
import time
import logging
import paramiko
from shutil import copyfile
from datetime import datetime
from picamera import PiCamera

time0 = time.time()
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
recTimeStamp = datetime.now().strftime("%y%m%d_%H%M")

"""
RaspBerry Pi Main Acquisition Script
Launched at startup after main.py which opens 3G & Inverse SSH

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
        logging.info("Sent {} to server".format(filepath))
        return True
    except Exception as e:
        logging.info("Cannot connect to server for {} : {}".format(filepath, type(e).__name__))
        return False


def sendMissingLogs():
    currentLogs = [f for f in list(os.walk(os.path.join(directory, "data")))[0][2] if "logMain" in f]

    # fixme: temporary for 1st launch; to remove:
    with open(os.path.join(directory, "data/logHistory.txt"), "w+") as f:
        f.write('\n'.join(currentLogs) + '\n')

    with open(os.path.join(directory, "data/logHistory.txt"), "r") as f:
        pastLogs = [l.replace("\n", "") for l in f.readlines()]

    logDiff = [f for f in currentLogs if f not in pastLogs]
    for fileName in logDiff:
        if not copyToServer("data/{}".format(fileName)):
            currentLogs.remove(fileName)
    with open(os.path.join(directory, "data/logHistory.txt"), "w+") as f:
        f.write('\n'.join(currentLogs) + '\n')


if __name__ == "__main__":
    time.sleep(5)
    autoShutdown = False
    launchCount = getLaunchCount()

    print("... Waiting for SecondaryPi's data.")

    timeAcq = time.time()
    acqTimeOut = 60
    fileDiff = []
    with open(os.path.join(directory, "data/fileHistory.txt"), "r") as f:
        pastFiles = [l.replace("\n", "") for l in f.readlines()]

    # todo to enable continuous acquisition: wait additional seconds when new data is sent. then compress and send.

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
            time.sleep(8)
            currentFiles = list(os.walk(os.path.join(directory, "dataSecondary")))[0][2]
            fileDiff = [f for f in currentFiles if f not in pastFiles]
        for fileName in fileDiff:
            sourcePath = os.path.join(directory, "dataSecondary/{}".format(fileName))
            copyfile(src=os.path.join(directory, "dataSecondary/{}".format(fileName)),
                     dst=os.path.join(directory, "data/{}".format(fileName)))
            if not copyToServer("data/{}".format(fileName)):
                currentFiles.remove(fileName)
            else:
                os.remove(sourcePath)
        with open(os.path.join(directory, "data/fileHistory.txt"), "w+") as f:
            f.write('\n'.join(currentFiles) + '\n')
        print("Data files ({}) sent to server: {}".format(len(fileDiff), fileDiff))
        autoShutdown = True

    logging.info("Acquistion time of {}s".format(time.time() - timeAcq))

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

    sendMissingLogs()

    copyToServer(logFilePath)

    if autoShutdown:
        time.sleep(10)
        os.system("sudo shutdown now")
