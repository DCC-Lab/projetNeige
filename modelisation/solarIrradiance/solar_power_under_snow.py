import numpy as np
import matplotlib.pylab as plt
from scipy.interpolate import interp1d
from datetime import datetime
from solarpy import irradiance_on_plane
from tartes import irradiance_profiles
from tartes.impurities import Soot
from matplotlib.colors import LogNorm


def colorPlot(Z, wavelength, depth, figtitle):
    Z = Z.T
    depth *= -100
    X, Y = np.meshgrid(wavelength, depth)
    fig = plt.figure()
    c = plt.pcolor(X, Y, Z, shading='auto', norm=LogNorm(vmin=Z.min(), vmax=Z.max()), cmap='PuBu_r')
    fig.colorbar(c)

    plt.title(figtitle)
    plt.ylabel('Depth into snow [cm]')
    plt.xlabel("Wavelength [nm]")
    plt.show()


def depthPlot(Z, wavelength, depth, Nplot):
    N_depth = len(depth)
    fig = plt.figure()
    for i in range(Nplot):
        depth_number = int(round(i * N_depth / Nplot))
        depth_i = depth[depth_number]
        plt.semilogy(wavelength, Z[:, depth_number], label='depth = %0.1f cm' % (-1 * depth_i))
    plt.legend()
    plt.xlabel("Wavelength [nm]")
    plt.title("Snow attenuation")
    plt.show()


def totalSolarIntensity(year=2021, month=2, date=26, hour=12, altitude=300, latitude=48):
    vnorm = np.array([0, 0, -1])  # plane pointing zenith
    date = datetime(year, month, date, hour, minute=0)
    TSA = irradiance_on_plane(vnorm, altitude, date, latitude)
    return TSA


def solarSpectrum(ROI=None, TSA=None):
    d = np.loadtxt('astmg173.csv', delimiter=';', skiprows=1, usecols=[0, 3])
    wave = d[:, 0]
    intensity = d[:, 1]

    if TSA is None:
        TSA = totalSolarIntensity()

    intensity *= TSA / np.sum(intensity)

    if ROI is None:
        return intensity
    else:
        f = interp1d(wave, intensity, kind='linear')
        return f(ROI)


def snowAttenuation(wavelengths, thickness, plot=False):
    depth = np.arange(0, thickness, 0.01)
    SSA = [15, 25, 60]
    density = [350, 300, 150]
    impurities = [10e-9, 10e-9, 10e-9]  # 10 ng/g de soot

    Id, Iu = irradiance_profiles(wavelengths * 1e-9, depth, SSA, density, thickness=thickness,
                                 impurities=impurities, impurities_type=Soot,
                                 soilalbedo=0.1, refrac_index="p2016")

    errX, errY = np.where(np.diff(Id, axis=1) > 0)
    for (w, d) in zip(errX, errY):
        Id[w, d+1] = np.min(Id[w])

    if plot:
        colorPlot(Id, wavelengths, depth, 'Attenuation sous la neige')
        depthPlot(Id, wavelengths, depth, 5)
    return np.swapaxes(Id, 0, 1)


if __name__ == '__main__':
    """ Distances in m. Wavelengths in nm. """

    wavelengths = np.arange(300, 1300, 1)

    sun = solarSpectrum(ROI=wavelengths)
    snow = snowAttenuation(wavelengths, thickness=0.5, plot=True)

    for d in np.arange(0, 30, 5):  # cm
        irradianceAtDepth = sun * snow[d]
        plt.plot(wavelengths, irradianceAtDepth, label='d = {}cm'.format(d))
    plt.ylabel("Spectral irradiance [W/m$^2$/nm]")
    plt.xlabel("Wavelength [nm]")
    plt.legend(loc='best')
    plt.show()
