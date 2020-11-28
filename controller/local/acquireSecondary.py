import os
import time
import logging
import paramiko
import numpy as np
from serial import Serial
from serial.tools import list_ports

"""
RaspBerry Pi Secondary Acquisition Script
Launched at startup

- For each COM, integrate signal for N points. Each COM corresponds to 4 PD.
- Save data to file
- Send data to main Pi over local SSH
"""

N = 100
nbOfAcquisition = 10
TEST = True

SERVER = "main.local"
USER = "pi"
PWD = "projetneige2020"

time0 = time.time()
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger("paramiko").setLevel(logging.WARNING)


def setupLogger(name, filePath, level=logging.INFO):
    l = logging.getLogger(name)
    formatter = logging.Formatter('%(message)s')
    fileHandler = logging.FileHandler(os.path.join(directory, filePath), mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


def readData(ser, N) -> (int, list):
    try:
        nanoID = None
        localData = []
        while len(localData) != N:
            line = ser.readline()
            line = line[0:len(line)-2].decode("utf-8", errors='replace')
            try:
                vector = [float(e) for e in line.split(',')]
                if len(vector) == 7:
                    nanoID = int(vector[0])
                    localData.append(vector[1:])
            except ValueError:
                continue
        return nanoID, np.asarray(localData)
    except Exception as e:
        logger.info("E.read: {}".format(type(e).__name__))


def acquireSensors(ports):
    logger.info(".Acq.")
    timeAcq = time.time()
    data = np.full((6*8, 2), np.NaN)
    for i, port in enumerate(ports):
        try:
            logger.info("P{}".format(i+1))
            timeSensor = time.time()
            s = Serial(port, baudrate=115200, timeout=3)
            s.flushInput()
            nanoId, raw = readData(ser=s, N=N)
            s.close()

            fillIdx = (nanoId - 1) * 6
            data[fillIdx: fillIdx+6, 0] = np.mean(raw, axis=0).round(2)
            data[fillIdx: fillIdx+6, 1] = np.std(raw, axis=0).round(2)
            logger.info("{}s".format(round(time.time()-timeSensor, 2)))

        except Exception as e:
            logger.info("E.port {} : {}".format(port, e))
            continue
    logger.info("AcqT = {}s ({} NaN)".format(round(time.time() - timeAcq), np.isnan(data).sum()))
    return data


def incrementLaunchCount():
    countPath = os.path.join(directory, "settings/count.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    return count


def loadMissingFiles():
    fileDiffPath = os.path.join(directory, "settings/fileDiff.txt")
    with open(fileDiffPath, "r") as f:
        fileDiff = [l.replace("\n", "") for l in f.readlines()]
    return [f for f in fileDiff if f]


def saveMissingFiles(fileDiff: list):
    fileDiffPath = os.path.join(directory, "settings/fileDiff.txt")
    with open(os.path.join(directory, fileDiffPath), "w+") as f:
        f.write('\n'.join(fileDiff))


def appendMissingFiles(filePaths):
    missingFiles = loadMissingFiles()
    missingFiles.extend(filePaths)
    saveMissingFiles(missingFiles)


def waitForConnection(attempts=20):
    timeCon = time.time()
    logger.info(".Connect.")
    for i in range(attempts):
        logger.info("{}/{}".format(i+1, attempts))
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(SERVER, username=USER, password=PWD, timeout=10)
            ssh.close()
            logger.info("ConT.={}s".format(round(time.time() - timeCon)))
            return 1
        except Exception as e:
            logger.info("E.SSH: {}".format(type(e).__name__))
            time.sleep(2)
    return 0


def copyToMain(filepath):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PWD, timeout=20)
        sftp = ssh.open_sftp()
        sftp.put(os.path.join(directory, filepath), os.path.join("/home/pi/Documents/projetNeige/controller", filepath))
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logger.info("E.Send {} : {}".format(filepath, type(e).__name__))
        return False


def copyFilesToMain():
    filesToSend = loadMissingFiles()
    logger.info("Sending {}: {}".format(len(filesToSend), [f.split("/")[-1].split(".")[0] for f in filesToSend]))

    try:  # should always work since we already tested the connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PWD, timeout=20)
        sftp = ssh.open_sftp()
    except Exception as e:
        logger.info("E.Transfer: {}".format(type(e).__name__))
        return

    newMissingFiles = []
    for i, filePath in enumerate(filesToSend):
        if filePath == logFilePath:
            logger.info("TT={}s".format(round(time.time() - time0)))
        try:
            sftp.put(os.path.join(directory, filePath), os.path.join("/home/pi/Documents/projetNeige/controller", filePath))
            logger.info("{}".format(i + 1))
        except Exception as e:
            logger.info("E.Send {} : {}".format(filePath, type(e).__name__))
            newMissingFiles.append(filePath)
    saveMissingFiles(newMissingFiles)
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    autoShutDown = False

    for _ in range(nbOfAcquisition):
        launchCount = incrementLaunchCount()
        logFilePath = "dataSecondary/SEC_{}.log".format(launchCount)

        setupLogger(str(launchCount), logFilePath)
        logger = logging.getLogger(str(launchCount))

        usbPorts = [e.device for e in list_ports.comports() if "USB" in e.device]
        if TEST:
            usbPorts = ['/dev/ttyACM0'] * 8
        logger.info("{} Ports".format(len(usbPorts)))

        data = acquireSensors(usbPorts)

        dataFilePath = "dataSecondary/PD_{}.txt".format(launchCount)
        np.savetxt(os.path.join(directory, dataFilePath), data)

        appendMissingFiles([dataFilePath, logFilePath])

        r = waitForConnection()
        if r:
            copyFilesToMain()

        if not np.isnan(data).any():
            autoShutDown = True

    if autoShutDown:
        os.system("sudo shutdown now")
