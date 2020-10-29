from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np


rawA = np.loadtxt('filter_raw_b390.csv', delimiter=',')
rawB = np.loadtxt('filter_raw_rg715.csv', delimiter=',')

xA = rawA[:, 0]
yA = np.clip(rawA[:, 1] / 100, 0, 1)
fA = interp1d(xA, yA, kind='linear')

xB = rawB[:, 0]
yB = np.clip(rawB[:, 1] / 100, 0, 1)
fB = interp1d(xB, yB, kind='linear')

wavelengths = np.arange(300, 1300, 1)
filterA_pre = fA(wavelengths[:900])
filterA = np.concatenate([filterA_pre, np.linspace(filterA_pre[-1], 0, 100)])
filterB = fB(wavelengths)

fig, [ax1, ax2] = plt.subplots(2, 1, sharey='all')
ax1.plot(wavelengths, filterA)
ax1.set_title('Filter B-390 attenuation')
ax2.plot(wavelengths, filterB)
ax2.set_title('Filter RG-715 attenuation')
plt.tight_layout()
plt.show()

# np.savetxt("filterSpectrumA.txt", filterA)
# np.savetxt("filterSpectrumB.txt", filterB)
