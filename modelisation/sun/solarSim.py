import numpy as np
from scipy.interpolate import interp1d
from datetime import datetime
from solarpy import irradiance_on_plane


def totalSolarIntensity(year=2021, month=2, date=26, hour=12, altitude=300, latitude=48):
    vnorm = np.array([0, 0, -1])  # plane pointing zenith
    date = datetime(year, month, date, hour, minute=0)
    TSA = irradiance_on_plane(vnorm, altitude, date, latitude)
    return TSA


def solarSpectrum(ROI=None, TSA=None):
    d = np.loadtxt('solarRef.csv', delimiter=';', skiprows=1, usecols=[0, 3])
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


if __name__ == '__main__':
    """ Distances in m. Wavelengths in nm. """

    wavelengths = np.arange(300, 1300, 1)

    sun = solarSpectrum(ROI=wavelengths)

    # np.savetxt('solarSpectrum.txt', sun)
