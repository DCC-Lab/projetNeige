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
from paramiko.ssh_exception import NoValidConnectionsError

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

N = 100
captureIntervals = 6

logFilePath = "dataSecondary/log_{}.log".format(recTimeStamp)
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(os.path.join(directory, logFilePath)), logging.StreamHandler()])

def read_data(ser, N) -> (int, list):
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

def copy_to_main(filepath, server="main.local", username="pi", mdp="projetneige2020"):
#def copy_to_main(filepath, server="169.254.219.87", username="marc-andrevigneault", mdp="Bonjour1!"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.load_host_keys(os.path.expanduser(os.path.join("/home", "pi", ".ssh", "known_hosts")))
    ssh.connect(server, username=username, password=mdp, timeout=20)
    sftp = ssh.open_sftp()
    #  /home/pi/Documents/projetNeige/controller"
    sftp.put(os.path.join(directory, filepath), os.path.join("/home/pi/Documents/projetNeige/controller", filepath))
    #sftp.put(os.path.join(directory, filepath), os.path.join("/Users/marc-andrevigneault/Documents/Github/DCCLAB/projetNeige/controller", filepath))
    sftp.close()
    ssh.close()
    #except Exception as e:
        #logging.info("Cannot connect to Main RPi for {} : {}".format(filepath, type(e).__name__))
        #logging.info(traceback.format_exec())

if __name__ == "__main__":
    ports = [e.device for e in list_ports.comports() if "USB" in e.device]
    logging.info("Available ports: {}".format(ports))
    logging.info("... Acquiring.")
    timeAcq = time.time()
    data = np.full(4*8, np.NaN)

    for port in ports:
        try:
            timeNano0 = time.time()
            s = Serial(port, baudrate=115200, timeout=3)
            s.flushInput()
            logging.info("... Port {}".format(port))
            nanoId, raw = read_data(ser=s, N=N)  # (N, 4)
            raw = np.mean(raw, axis=0)  # (4,)
            fillIdx = (nanoId - 1) * 4
            data[fillIdx: fillIdx+4] = raw
            s.close()
            timeNano1 = time.time()
            logging.info("Acquisition time on '{}' of {}s".format(str(port), (timeNano1-timeNano0)))

        except Exception as e:
            logging.info("Error with port {} : {}".format(port, e))
            continue

    dataFilePath = "dataSecondary/PD_{}.txt".format(recTimeStamp)
    np.savetxt(os.path.join(directory, dataFilePath), data)

    logging.info("Acquistion time of {}s, data shape {}".format(time.time() - timeAcq, data.shape))
    logging.info("... Saved to disk.")

    # Transfer to Main RPi

    SSHRetry = 3
    failed = True
    for i in range(SSHRetry):
        logging.info("TRANSFER INITIALIZATION - TRY#{}".format(i))
        if failed:
            try:
                dataTransferTime0 = time.time()
                copy_to_main(dataFilePath)
                logging.info("data transfer time: {}s".format(time.time()-dataTransferTime0))
                logging.info("... Data saved to server.")
                logTransferTime0 = time.time()
                copy_to_main(logFilePath)
                logging.info("log transfer time: {}s".format(time.time()-logTransferTime0))
                logging.info("Total elapsed time = {}s".format(time.time() - time0))
                failed = False
                logging.info("Sucessful SSH data transfer.")
                break
            except Exception as e:
                logging.info("SSH connection has failed. Launching retry in 10 seconds.")
                logging.info(e)
                time.sleep(10)
                failed = True
                logging.info("Retrying...")
    # os.system("shutdown now")


