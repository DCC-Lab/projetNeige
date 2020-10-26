import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

u = 1*10**-6
M = 1*10**6

# RF Filter for preamp Op-Amp

Rf = 1*M
Cf = 1*u
w = np.linspace(1, 60, 100)

Xr = Rf
Xc = (1/(Cf*1j*w))
Xt = 1/((1/Xr) + (1/Xc))

reel = np.real(Xt)
imag = np.imag(Xt)
norm = np.abs(Xt)

scale_factor = 10**3
fmt = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_factor))

fig, ax = plt.subplots(2, 1)
ax[0].plot(w, norm, linewidth=0.8, label=r"$X_T(\omega)=\frac{1}{\frac{1}{R}+Cj\omega}$")
ax[0].plot([], [], ' ', label="R=1M$\Omega$, C=1$\mu$F")
ax[0].yaxis.set_major_formatter(fmt)
ax[0].set_xlabel("Frequency $\omega$ (rad/s)")
ax[0].set_ylabel(r"Impedance ($\Omega$) $\times 10^3$")
ax[0].legend()

# Low-pass Filter post-preamp

Rlp = 10000
Clp = 1*u
w = np.linspace(0, 200, 10000)

Xr = Rlp
Xc = (1/(Clp*1j*w))
Xt = Xr + Xc
Hw = 1 - Xr/Xt

reel = np.real(Xt)
imag = np.imag(Xt)
norm = np.abs(Xt)

ax[1].plot(w, 20*np.log10(Hw), linewidth=0.8, label=r"$H(\omega)=1-\frac{R}{R+\frac{1}{R}+Cj\omega}$")
ax[1].plot([], [], ' ', label="R=10k$\Omega$, C=1$\mu$F")
ax[1].set_xlabel("Frequency $\omega$ (rad/s)")
ax[1].set_ylabel(r"Gain (dB)")
ax[1].legend()

# Plot

plt.tight_layout()
plt.show()
