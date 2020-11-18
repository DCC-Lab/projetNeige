"""
RaspBerry Pi Acquisition Script
Launched at startup

1. Check for Git updates (?)
2. For each COM, integrate signal for N points. Each COM corresponds to 4 PD.
3. Save data to file
4. If time to take a picture (count or RTC check), take a CAM pic, compress it and save it.
5. Send generated data over SSH
"""
import os
import paramiko
import numpy as np
from serial import Serial
from datetime import datetime
from serial.tools import list_ports


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


# public 24.201.18.112, lan 192.168.0.188 
def copyToServer(filepath, server="192.168.0.188", username="Alegria"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server, username=username)
    sftp = ssh.open_sftp()
    sftp.put(os.path.join(os.getcwd(), filepath), os.path.join("C:/SnowOptics", filepath))
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    
    # nanoPorts = [e.device for e in list_ports.comports()]
    nanoPorts = ['/dev/ttyACM0']

    nanoPorts *= 4  # duplicate single COM into 4 for testing
    N = 100

    data = []
    for port in nanoPorts:
        s = Serial(port, baudrate=115200)
        s.flushInput()

        raw = np.asarray(readData(ser=s, N=N))
        data.append(raw)
        s.close()

    data = np.concatenate(data, axis=1)  # shape (N, 16)
    data = np.mean(data, axis=0)  # shape (16,)

    filepath = "data/PD_{}.txt".format(datetime.now().strftime("%y%m%d_%H%M"))
    np.savetxt(filepath, data)

    copyToServer(filepath)
