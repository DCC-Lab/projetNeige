from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np


raw = np.loadtxt('pd_raw.csv', delimiter=',')
x = raw[:, 0]
y = np.clip(raw[:, 1], 0, 1)
f = interp1d(x, y, kind='linear')

wavelengths = np.arange(300, 1300, 1)
diode_pre = f(wavelengths[105:780])
diode = np.concatenate([np.linspace(0, diode_pre[0], 105), diode_pre, np.linspace(diode_pre[-1], 0, 40), np.zeros(180)])

plt.plot(wavelengths, diode)
plt.title('Diode attenuation')
plt.ylim(0)
plt.show()

# np.savetxt("diodeSpectrum.txt", diode)
