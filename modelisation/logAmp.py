import numpy as np
import matplotlib.pyplot as plt

""" Model a log amplifier for a specific range of input voltage mapped to an ADC """

# input voltage
vmin = 8 * 10**(-6)  # V
vmax = 12000 * 10**(-6)  # V

# ADC specs
vmaxADC = 5  # V
n_bits = 10  # bit
LSB_error = 2  # bit
N = 100  # optional, used to compute an effective uncertainty for LSB_error over N samples

res = 2**n_bits
K = vmaxADC / np.log(vmax/vmin)
vin = np.linspace(vmin, vmax, 100000)

vout = K * np.log(vin/vmin)

# inverse function vin(vout) called x(y). used for plotting
y = np.linspace(0, vmaxADC, res)
x = vmin * np.exp(y / K)

plt.plot(vin, vout, linewidth=0.5)
plt.plot(x, y, marker='.', linestyle='', color='r', markersize=1.5)
plt.xlabel("V_in")
plt.ylabel("V_out")

print("K = ", round(K, 4))
print("Log denominator (R*I_s) = ", vmin)
rel_error = round((x[1]-x[0]) / x[0] * 100, 3)
print("Instantaneous Relative Uncertainty = {} %".format(rel_error * 2 ** LSB_error))
print("Averaged Relative Uncertainty (N={}) = {:.2f} %".format(N, rel_error * (2 ** (LSB_error / np.sqrt(N)))))
print("Relative Uncertainty = {} %".format(rel_error))

plt.show()
