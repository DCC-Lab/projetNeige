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
nbOfAcquisition = 1

SERVER = "main.local"
USER = "pi"
PWD = "projetneige2020"

time0 = time.time()
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        logging.info("Error reading data: {}".format(e))


def acquireSensors(ports):
    logging.info("... Acquiring.")
    timeAcq = time.time()
    data = np.full((4*8, 2), np.NaN)
    for port in ports:
        try:
            logging.info("... Port {}".format(port))
            timeSensor = time.time()
            s = Serial(port, baudrate=115200, timeout=3)
            s.flushInput()
            nanoId, raw = readData(ser=s, N=N)
            s.close()

            fillIdx = (nanoId - 1) * 4
            data[fillIdx: fillIdx+4, 0] = np.mean(raw, axis=0)
            data[fillIdx: fillIdx+4, 1] = np.std(raw, axis=0)
            logging.info("Acquisition time on '{}' of {}s".format(str(port), round(time.time()-timeSensor, 2)))

        except Exception as e:
            logging.info("Error with port {} : {}".format(port, e))
            continue
    logging.info("Acquistion time of {}s with {} missing values.".format(round(time.time() - timeAcq),
                                                                         np.isnan(data).sum()))
    return data


def incrementLaunchCount():
    countPath = os.path.join(directory, "data/count.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    return count


def loadMissingFiles():
    fileDiffPath = os.path.join(directory, "dataSecondary/fileDiff.txt")
    with open(fileDiffPath, "r") as f:
        fileDiff = [l.replace("\n", "") for l in f.readlines()]
    return fileDiff


def saveMissingFiles(fileDiff: list):
    fileDiffPath = os.path.join(directory, "dataSecondary/fileDiff.txt")
    with open(os.path.join(directory, fileDiffPath), "w+") as f:
        f.write('\n'.join(fileDiff) + '\n')


def appendMissingFiles(filePaths):
    missingFiles = loadMissingFiles()
    missingFiles.extend(filePaths)
    saveMissingFiles(missingFiles)


def waitForConnection(attempts=8):
    timeCon = time.time()
    for i in range(attempts):
        logging.info("... Connecting to main - Try {}".format(i+1))
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(SERVER, username=USER, password=PWD, timeout=20)
            ssh.close()
            logging.info("Successful SSH Connection in {}s".format(round(time.time() - timeCon)))
            return 1
        except Exception as e:
            logging.info("SSH connection has failed.")
            if i < (attempts-1):
                logging.info("Launching retry in 3 seconds.")
            logging.info(e)
            time.sleep(3)
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
        logging.info("Cannot connect to server for {} : {}".format(filepath, type(e).__name__))
        return False


def copyFilesToMain():
    filesToSend = loadMissingFiles()
    logging.info("Sending files to main ({}): {}".format(len(filesToSend), filesToSend))

    try:  # should always work since we already tested the connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PWD, timeout=20)
        sftp = ssh.open_sftp()
    except Exception as e:
        logging.info("Cannot init file transfer: {}".format(e))
        return

    newMissingFiles = []
    for filePath in filesToSend:
        if filePath == logFilePath:
            logging.info("Total elapsed time = {}s".format(time.time() - time0))
            logging.info("Successful SSH data transfer.")
        try:
            sftp.put(os.path.join(directory, filePath), os.path.join("/home/pi/Documents/projetNeige/controller", filePath))
        except Exception as e:
            logging.info("Cannot send file {} : {}".format(filePath, e))
            newMissingFiles.append(filePath)
    saveMissingFiles(newMissingFiles)
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    autoShutDown = False

    for _ in range(nbOfAcquisition):
        launchCount = incrementLaunchCount()
        logFilePath = "dataSecondary/log_{}.log".format(launchCount)
        logging.basicConfig(level=logging.INFO,
                            handlers=[logging.FileHandler(os.path.join(directory, logFilePath)), logging.StreamHandler()])

        usbPorts = [e.device for e in list_ports.comports() if "USB" in e.device]
        logging.info("Available ports: {}".format(usbPorts))

        data = acquireSensors(usbPorts)

        dataFilePath = "dataSecondary/PD_{}.txt".format(launchCount)
        np.savetxt(os.path.join(directory, dataFilePath), data)
        logging.info("Data saved to disk.")

        appendMissingFiles([dataFilePath, logFilePath])

        waitForConnection()
        copyFilesToMain()

        if not np.isnan(data).any():
            autoShutDown = True

    if autoShutDown:
        os.system("sudo shutdown now")
