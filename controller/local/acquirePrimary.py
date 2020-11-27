import os
import time
import logging
import paramiko
from shutil import copyfile
from datetime import datetime
from picamera import PiCamera

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
RaspBerry Pi Main Acquisition Script
Launched at startup after main.py which opens 3G & Inverse SSH

- Wait for Secondary Pi's data
- Take picture if it's time to (interval check)
- Send data, image and logs to SERVER over SSH
- Auto shutdown if no backdoor enabled
"""

nbOfAcquisition = 1
captureIntervals = 6

SERVER = "24.201.18.112"
USER = "Alegria"


def print(s):
    logging.info(s)


def setupLogger(filePath):
    logging.basicConfig(format='%(message)s', level=logging.INFO,
                        handlers=[logging.FileHandler(os.path.join(directory, filePath)),
                                  logging.StreamHandler()])
    logging.getLogger("paramiko").setLevel(logging.WARNING)


def getLaunchCount():
    countPath = os.path.join(directory, "settings/count.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    return count


def backdoorState():
    filePath = os.path.join(directory, "settings/backdoor.txt")
    with open(filePath, "r") as f:
        state = int(f.readlines()[0])
    return state


def capture(filepath):
    camera = PiCamera()
    camera.capture(filepath)


def loadPastFiles():
    with open(os.path.join(directory, "settings/fileHistory.txt"), "r") as f:
        files = [l.replace("\n", "") for l in f.readlines()]
    return files


def loadCurrentFiles():
    return list(os.walk(os.path.join(directory, "dataSecondary")))[0][2]


def listenForNewFiles(initialTimeOut=60, streamTimeOut=4):
    print(".Listening.")
    listenTime0 = time.time()
    pastFiles = loadPastFiles()
    newFiles = []

    deltaAcq = 0
    while len(newFiles) == 0 and deltaAcq < initialTimeOut:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        time.sleep(1)
        deltaAcq += 1

    if len(newFiles) == 0:
        print("E.Timeout")
        return

    lastLength = 0
    while len(newFiles) > lastLength:
        lastLength = len(newFiles)
        print("Stream_0: {} files".format(lastLength))
        for i in range(10):
            time.sleep(streamTimeOut/10)
            newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
            print("Stream_{}: {} files".format(i+1, len(newFiles)))
    print("ListenTime={}s".format(round(time.time() - listenTime0)))

    return newFiles


# public 24.201.18.112, lan 192.168.0.188
def copyToServer(filepath):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(SERVER, username=USER)
        sftp = ssh.open_sftp()
        sftp.put(os.path.join(directory, filepath), os.path.join("C:/SnowOptics", filepath))
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logging.info("E.Send {} : {}".format(filepath, type(e).__name__))
        return False


def copySecondaryFilesToServer(files):
    currentFiles = loadCurrentFiles()

    print(".Sending {}: {}".format(len(files), files))

    try:  # should always work since we already tested the connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(SERVER, username=USER)
        sftp = ssh.open_sftp()
    except Exception as e:
        logging.info("E.SSH: {}".format(type(e).__name__))
        return

    for i, fileName in enumerate(files):
        sourcePath = os.path.join(directory, "dataSecondary/{}".format(fileName))
        copyfile(src=os.path.join(directory, "dataSecondary/{}".format(fileName)),
                 dst=os.path.join(directory, "data/{}".format(fileName)))
        try:
            sftp.put(os.path.join(directory, "data/{}".format(fileName)),
                     os.path.join("/home/pi/Documents/projetNeige/controller", "data/{}".format(fileName)))
            currentFiles.remove(fileName)
            os.remove(sourcePath)
            logging.info("Sent {}".format(i + 1))

        except Exception as e:
            logging.info("E.Send {} : {}".format(fileName, type(e).__name__))

    with open(os.path.join(directory, "settings/fileHistory.txt"), "w+") as f:
        f.write('\n'.join(currentFiles) + '\n')

    sftp.close()
    ssh.close()


def sendMissingLogs():
    currentLogs = [f for f in list(os.walk(os.path.join(directory, 'data')))[0][2] if '.log' in f]
    currentLogs = [f for f in currentLogs if ('logMAIN' in f or 'logCON' in f)]

    with open(os.path.join(directory, "settings/logHistory.txt"), "r") as f:
        pastLogs = [l.replace("\n", "") for l in f.readlines()]

    logDiff = [f for f in currentLogs if f not in pastLogs]
    print(".Sending {}: {}".format(len(logDiff), logDiff))
    for i, fileName in enumerate(logDiff):
        if not copyToServer("data/{}".format(fileName)):
            currentLogs.remove(fileName)
        else:
            logging.info("Sent {}".format(i + 1))
    with open(os.path.join(directory, "settings/logHistory.txt"), "w+") as f:
        f.write('\n'.join(currentLogs) + '\n')


if __name__ == "__main__":
    autoShutdown = False

    for _ in range(nbOfAcquisition):
        time0 = time.time()
        recTimeStamp = datetime.now().strftime("%y%m%d_%H%M")
        logFilePath = "data/logMAIN_{}.log".format(recTimeStamp)

        setupLogger(logFilePath)
        launchCount = getLaunchCount()

        fileDiff = listenForNewFiles(initialTimeOut=60, streamTimeOut=5)

        copySecondaryFilesToServer(fileDiff)

        if launchCount % captureIntervals == 0:
            try:
                imageFilePath = "data/image_{}.jpg".format(recTimeStamp)
                capture(os.path.join(directory, imageFilePath))
                copyToServer(imageFilePath)
                print("Sent image")
            except Exception as e:
                logging.info("E.Cam: {}".format(type(e).__name__))

        if len(fileDiff) > 0:
            autoShutdown = True

        if backdoorState() == 1:
            logging.info("BD UP")
            autoShutdown = False

        logging.info("TotTime={}s, shutdown={}".format(round(time.time() - time0), autoShutdown))

        sendMissingLogs()

    if autoShutdown:
        time.sleep(10)
        os.system("sudo shutdown now")
