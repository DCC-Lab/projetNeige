import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

""" Model a photodiode response curve of different parameters"""

kb = const.k     # Boltzmann constant ()
q = const.e      # elementary charge (C)
T = 258.0               # Temperature (°K)
Vt = kb * T / q         # Thermal Voltage (V)
print(Vt)
Id = 1 * 10**-9         # Dark current (A)
Phi = 1 * 10**-6        # Radiant Flux (W)
rPhi = 0.22             # Efficiency (A/W)

flux = np.linspace(Phi, 1000*Phi, 2000)
Vp = Vt*np.log(flux * rPhi / Id)

plt.semilogx(flux, Vp, linewidth=0.8)
plt.xlabel("Light Power (W)")
plt.ylabel("Diode Generated Voltage (V)")
plt.show()
