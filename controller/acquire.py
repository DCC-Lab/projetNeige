"""
RaspBerry Pi Acquisition Script
Launched at startup

1. Check for Git updates (?)
2. For each COM, integrate signal for N points. Each COM corresponds to 4 PD.
3. Save data to file
4. If time to take a picture (count or RTC check), take a CAM pic, compress it and save it.
5. Send generated data over SSH
"""

import numpy as np
from serial import Serial
from serial.tools import list_ports
from controller.utils import readData, copyToServer
from datetime import datetime


# nanoPorts = [e.device for e in list_ports.comports()]
nanoPorts = ["COM3"] * 4
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
