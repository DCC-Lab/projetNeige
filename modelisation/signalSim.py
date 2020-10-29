import matplotlib.pyplot as plt
import numpy as np


def fiberAttenuation(d, alpha=0.2):
    return 10 ** (-alpha*d / 10)


# Components
wavelengths = np.arange(300, 1300, 1)
sun = np.loadtxt('sun/solarSpectrum.txt')
snow = np.loadtxt('snow/snowAttenuation.txt')
filterA = np.loadtxt('filters/filterSpectrumA.txt')
filterB = np.loadtxt('filters/filterSpectrumB.txt')
diode = np.loadtxt('diode/diodeSpectrum.txt')
diodeSurface = 7 * 10 ** (-6)


if __name__ == '__main__':

    depths = [0, 10, 20]
    fiberLength = 2

    fs = 16
    fiber = fiberAttenuation(d=fiberLength)
    fig, axes = plt.subplots(len(depths), 4, sharex='all', sharey='row')

    for i, depth in enumerate(depths):
        axes[i, 0].plot(wavelengths, sun, color='k')
        axes[i, 0].text(-400, max(sun)/2, "{} cm".format(depth), fontsize=20)

        axes[i, 1].plot(wavelengths, sun * snow[depth], color='dimgray')

        signalBlue = sun * snow[depth] * fiber * filterA
        signalRed = sun * snow[depth] * fiber * filterB
        axes[i, 2].plot(wavelengths, signalBlue, color='tab:blue')
        axes[i, 2].plot(wavelengths, signalRed, color='tab:red')

        signalBlue *= diode
        signalRed *= diode
        microWattsBlue = np.sum(signalBlue) * diodeSurface * 10 ** 6
        microWattsRed = np.sum(signalRed) * diodeSurface * 10 ** 6
        axes[i, 3].plot(wavelengths, signalBlue, color='tab:blue', label="{} uW".format(round(microWattsBlue, 1)))
        axes[i, 3].plot(wavelengths, signalRed, color='tab:red', label="{} uW".format(round(microWattsRed, 1)))
        axes[i, 3].legend(loc='best', fontsize=fs)

    axes[0, 0].set_title("Surface", fontsize=fs)
    axes[0, 1].set_title("+ Snow", fontsize=fs)
    axes[0, 2].set_title("+ Fiber (2m) + Filters", fontsize=fs)
    axes[0, 3].set_title("+ Diode", fontsize=fs)
    axes[-1, 0].set_ylabel("Spectral irradiance [W/m$^2$/nm]", fontsize=fs)
    axes[-1, 0].set_xlabel("Wavelength [nm]", fontsize=fs)
    plt.show()
