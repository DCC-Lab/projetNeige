import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

""" Model a photodiode response curve of different parameters"""

lux = [58.3, 46.6, 38.8, 30.0, 19.6, 3.1, 2.7]
voltage = [4.85, 4.00, 3.37, 2.65, 1.75, 0.43, 0.395]
noize = [8.25, 10.0, 10.8, 10.6, 9.2, 5.0, 4.5]

plt.plot(lux, voltage, linewidth=0.8)
plt.xlabel("Light Power (Lux)")
plt.ylabel("Amplified Diode Voltage (V)")
plt.show()
