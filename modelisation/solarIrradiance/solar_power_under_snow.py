import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from scipy.interpolate import interp1d
from datetime import datetime
from solarpy import irradiance_on_plane
from tartes import irradiance_profiles
from tartes.impurities import Soot
from matplotlib.colors import LogNorm

# etapes
# 1 simuler lirradiance solaire au sol
# 2 faire passer dans Tartes a 2 couches
# 3 utiliser des parametres de fibre optique/detecteur

def colorplot(Z, wavelength, depth, figtitle):
    Z = Z.T
    depth *= -100
    wavelength *= 1e9
    X, Y = np.meshgrid(wavelength,depth)
    fig = plt.figure()
    c = plt.pcolor(X, Y, Z, shading='auto', norm=LogNorm(vmin=Z.min(), vmax=Z.max()), cmap='PuBu_r')
    fig.colorbar(c)

    plt.title(figtitle)
    plt.ylabel('Depth into snow [cm]')
    plt.xlabel("Wavelength [nm]")
    plt.show()

def depthplot(Z, wavelength, depth, Nplot):

    N_depth = len(depth)
    fig = plt.figure()
    for i in range(Nplot):
        depth_number = int(round(i*N_depth/Nplot))
        depth_i = depth[depth_number]
        plt.semilogy(wavelength, Z[:, depth_number], label='depth = %0.1f cm' %(-1*depth_i))
    plt.legend()
    plt.ylabel(r'Downwelling Power [$\rm {Wmm^{-2}nm^{-1}}$]', size=16)
    plt.xlabel("Wavelength [nm]", size=16)
    plt.title("Solar power under snow")
    plt.show()



def solarIntensity(year, month, date, hour, minute, altitude, latitude=48):
    # sor la TSA (Total solar irradiance)
    vnorm = np.array([0, 0, -1])  # plane pointing zenith
    date = datetime(year, month, date, hour, minute)
    TSA = irradiance_on_plane(vnorm, altitude, date, latitude)
    TSA *= 1e-6 # pour l'avoir en W/mm^2
    return TSA

def solarSpectrum(wavelength, TSA=1000, plot=False):
    # sort l'energie solaire en fonction du spectre
    # tout est en nm

    # telecharge un fichier de AM1.5
    df = pd.read_csv('astmg173.csv', sep=';') #https://www.nrel.gov/grid/solar-resource/spectra-am1.5.html
    wvl = np.array(df['Wvlgth nm'])
    I = np.array(df['Direct+circumsolar W*m-2*nm-1'])
    for count, wl in enumerate(wvl):
        wvl[count] = float(wl)
        I[count] = float(I[count])
    I = I/sum(I)*TSA # calcule l'intensité en fonction du TSA
    # calcule l'intensite pour chaque bande
    f = interp1d(wvl, I, kind='linear')
    xnew = wavelength
    spectre_my_wvl = f(xnew)

    if plot:
        plt.figure(1)

        plt.plot(wvl, I, color ='k')
        plt.plot(wavelength, spectre_my_wvl, color='r')
        plt.savefig('figure_out/solar_spectrum.png')
    return spectre_my_wvl



def snow_attenuation(flux, depth, wavelength, SSA, density, thickness, impurities, plot=True):
    Id, Iu = irradiance_profiles(wavelength, depth, SSA, density, thickness=thickness,
           impurities=impurities, impurities_type=Soot,
           soilalbedo=0.1, dir_frac=0.0, totflux=flux, refrac_index="p2016")
    if plot:
        colorplot(Id, wavelength, depth, 'Flux sous la neige [W/mm^2/nm')
        depthplot(Id, wavelength, depth, 5)
    return Id, Iu
"""
filt_central_wvl = [425, 720]
filt_bandwidth = [80, 60]
year = 2021
month = 5
date = 1
hour = 12
minute = 0
altitude = 300

TSA = solarIntensity(year, month, date, hour, minute, altitude, latitude=48)
I_band = solarSpectrum(filt_central_wvl, filt_bandwidth, TSA=TSA, plot=True)
print(TSA)#: 788.9574243565424 W/m^2
print(I_band)#: 0.43230329 W/m^2 0.95512381 W/m^2
"""
filt_central_wvl = np.array([400, ])
filt_bandwidth = [80, 60]
year = 2021
month = 2
date = 26
hour = 12
minute = 0
altitude = 300
wavelength_nm = np.arange(400, 900, 25)

# ensoleillement sur tout le spectre
TSA = solarIntensity(year, month, date, hour, minute, altitude, latitude=48)

#intensite par bande de filtres
spectre = solarSpectrum(wavelength=wavelength_nm, TSA=TSA, plot=True)

#snow attenuation
wavelength = wavelength_nm*1e-9
thickness = [0.5, 0.5, 1.0] #3 couches de 1m base sur les condition de fevrier 2019
SSA = [15, 25, 60]
density = [350, 300, 150]
impurities = [10e-9, 10e-9, 10e-9] # 10 ng/g de soot
depth = np.arange(0, 0.5, 0.05)

Id, Iu = snow_attenuation(spectre, depth, wavelength, SSA, density, thickness, impurities, plot=True)


