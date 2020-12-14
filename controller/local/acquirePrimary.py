import os
import time
import logging
import paramiko
from shutil import copyfile
from datetime import datetime
from picamera import PiCamera

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger("paramiko").setLevel(logging.WARNING)

"""
RaspBerry Pi Main Acquisition Script
Launched at startup after main.py which opens 3G & Inverse SSH

- Wait for Secondary Pi's data
- Take picture if it's time to (interval check)
- Send data, image and logs to SERVER over SSH
- Auto shutdown if no backdoor enabled
"""

nbOfAcquisition = 20
captureIntervals = 6

SERVER = "24.201.18.112"
USER = "Alegria"
camera = PiCamera()
camera.led = False
camera.hflip = True


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


def print(s):
    return logger.info(s)


def getLaunchCount():
    countPath = os.path.join(directory, "settings/launchCount.txt")
    with open(countPath, "r") as f:
        count = int(f.readlines()[0])
    with open(countPath, "w+") as f:
        f.write(str(count+1) + "\n")
    return count


def getAcqCount():
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


def capture(filepath, lowRes=False):
    if lowRes:
        camera.resolution = (344, 200)
        camera.capture(filepath, quality=12)
    else:
        camera.resolution = (1920, 1080)
        camera.capture(filepath)


def loadPastFiles():
    with open(os.path.join(directory, "settings/fileHistory.txt"), "r") as f:
        files = [l.replace("\n", "") for l in f.readlines()]
    return files


def loadCurrentFiles():
    return list(os.walk(os.path.join(directory, "dataSecondary")))[0][2]


def listenForNewFiles(initialTimeOut):
    print(".Listening.")
    pastFiles = loadPastFiles()
    newFiles = []

    deltaAcq = 0
    while len(newFiles) == 0 and deltaAcq < initialTimeOut:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        time.sleep(0.2)
        deltaAcq += 0.2

    if len(newFiles) == 0:
        print("E.Timeout")

    else:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        print("L.T.={}s".format(deltaAcq))

    return newFiles


# public 24.201.18.112, lan 192.168.0.188
def copyToServer(filepath, tag = None):
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
        fileName = tag if tag is not None else filepath
        if type(e) == OSError:
            logger.info("EO.{}".format(fileName))
        else:
            logger.info("E.{} : {}".format(fileName, type(e).__name__))
        return False


def copySecondaryFilesToServer(files):
    currentFiles = loadCurrentFiles()

    print(".Sending {}: {}".format(len(files), [f.split(".")[0] for f in files]))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(SERVER, username=USER)
        sftp = ssh.open_sftp()
    except Exception as e:
        logger.info("E.SSH: {}".format(type(e).__name__))
        return

    for i, fileName in enumerate(files):
        sourcePath = os.path.join(directory, "dataSecondary/{}".format(fileName))
        copyfile(src=sourcePath, dst=os.path.join(directory, "data/{}".format(fileName)))
        try:
            sftp.put(os.path.join(directory, "data/{}".format(fileName)),
                     os.path.join("C:/SnowOptics", "data/{}".format(fileName)))
            currentFiles.remove(fileName)
            os.remove(sourcePath)
            logger.info("{}".format(i + 1))

        except Exception as e:
            logger.info("E.Send {} : {}".format(fileName, type(e).__name__))

    with open(os.path.join(directory, "settings/fileHistory.txt"), "w+") as f:
        f.write('\n'.join(currentFiles) + '\n')

    sftp.close()
    ssh.close()


def sendMissingLogs():
    currentLogs = [f for f in list(os.walk(os.path.join(directory, 'data')))[0][2] if '.log' in f]
    currentLogs = [f for f in currentLogs if ('SEC' not in f)]

    with open(os.path.join(directory, "settings/logHistory.txt"), "r") as f:
        pastLogs = [l.replace("\n", "") for l in f.readlines()]

    logDiff = [f for f in currentLogs if f not in pastLogs]
    print(".Sending {}: {}".format(len(logDiff), [l.split(".")[0] for l in logDiff]))
    for i, fileName in enumerate(logDiff):
        if not copyToServer("data/{}".format(fileName, tag=i)):
            currentLogs.remove(fileName)
        else:
            logger.info("{}".format(i + 1))
    with open(os.path.join(directory, "settings/logHistory.txt"), "w+") as f:
        f.write('\n'.join(currentLogs) + '\n')


def sendMissingImages():
    missingImages = loadMissingImages()
    if not missingImages:
        return
    print(".Sending Im {}: {}".format(len(missingImages), [l.split(".")[0] for l in missingImages]))
    for i, filePath in enumerate(missingImages):
        if copyToServer(filePath):
            missingImages.remove(filePath)
            logger.info("{}".format(i + 1))
        else:
            logger.info("E{}".format(i + 1))
    saveMissingImages(missingImages)


def loadMissingImages():
    fileDiffPath = os.path.join(directory, "settings/imDiff.txt")
    with open(fileDiffPath, "r") as f:
        fileDiff = [l.replace("\n", "") for l in f.readlines()]
    return [f for f in fileDiff if f]


def saveMissingImages(fileDiff: list):
    fileDiffPath = os.path.join(directory, "settings/imDiff.txt")
    with open(os.path.join(directory, fileDiffPath), "w+") as f:
        f.write('\n'.join(fileDiff))


def appendMissingImages(filePath):
    missingFiles = loadMissingImages()
    missingFiles.append(filePath)
    saveMissingImages(missingFiles)


if __name__ == "__main__":
    autoShutdown = False
    launchCount = getLaunchCount()

    for _ in range(nbOfAcquisition):
        time0 = time.time()
        recTimeStamp = datetime.now().strftime("%m%d%H%M")
        acqCount = getAcqCount()

        logFilePath = "data/MAN_{}.log".format(acqCount)

        setupLogger(str(acqCount), logFilePath)
        logger = logging.getLogger(str(acqCount))

        fileDiff = listenForNewFiles(initialTimeOut=60)

        copySecondaryFilesToServer(fileDiff)

        time.sleep(8)

        if launchCount % captureIntervals == 0 and acqCount == 0:
            imageFilePath = "data/IM_{}.jpg".format(acqCount)
            try:
                capture(os.path.join(directory, imageFilePath))
                copyToServer(imageFilePath)
                print("S.Im")
            except Exception as e:
                logger.info("E.Cam: {}".format(type(e).__name__))
                appendMissingImages(imageFilePath)

        imageFilePath = "data/IML_{}.jpg".format(acqCount)
        try:
            capture(os.path.join(directory, imageFilePath), lowRes=True)
            copyToServer(imageFilePath)
            print("S.Iml")
        except Exception as e:
            logger.info("E.LCam: {}".format(type(e).__name__))
            appendMissingImages(imageFilePath)

        time.sleep(2)

        if len(fileDiff) > 0:
            autoShutdown = True

        if backdoorState() == 1:
            logger.info("BD UP")
            autoShutdown = False

        logger.info("{}s, Shut={}".format(round(time.time() - time0), autoShutdown))

        time.sleep(2)

        sendMissingImages()
        sendMissingLogs()

    if autoShutdown:
        time.sleep(10)
        os.system("sudo shutdown now")
