import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import colorConverter as cc
import numpy as np
import glob
import re
import os
pwd = os.getcwd()
import itertools

jeff = True

## make background M^-2 contours
def plotBackground(ax, x0, y0, colour):
    cmap=makeCmap(colour,'backgroundColour')
    yMin=y0*np.power(x0/1e20,1)
    yMax=y0*np.power(x0/1e-20,1)
    nColours=25
    change=0.01
    for i in range(nColours):
        ax.fill([1e-20,1e-20,1e20],[yMax*change**i, yMin*change**i, yMin*change**i], c=cmap((i+1)/nColours), zorder=i + 1 - 100)

def makeCmap(hexColour, name, zeroColour='#FFFFFF'):
    r0,g0,b0=mpl.colors.hex2color(zeroColour)
    r,g,b=mpl.colors.hex2color(hexColour)
    cdict = {'red':   ((0.0, r0, r0),
                      (1.0, r, r)),
             'green': ((0.0, g0, g0),
                      (1.0, g, g)),
             'blue':  ((0.0, b0, b0),
                      (1.0, b, b))
            }
    cmap = mpl.colors.LinearSegmentedColormap(name, cdict)
    return cmap


gs = GridSpec(1, 1, bottom=.12, top=.95, left=.1, right=.98, hspace=0)
if jeff: fig = plt.figure(figsize=(10, 4))
else: fig = plt.figure(figsize=(11.69, 8.27))

#fig = plt.figure()
ax1 = fig.add_subplot(gs[0])

xlo, xhi = 1e-6, 1e16
ylo, yhi = 1e-33, 1e0
M_all = np.array([xlo, xhi])
#M_all = np.logspace(xlo, xhi, 500)

plotBackground(ax1, xhi*1e12, ylo, '#011627')

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(xlo, xhi)
ax1.set_ylim(ylo, yhi)
ax1.set_xlabel(r'Mass [M$_\odot]$')
ax1.set_ylabel(r'Number density, $dN / dV$ [pc$^{-3}]$')


## Planck cosmology
Omh2 = 0.143
Och2 = 0.12
Obh2 = 0.0237
H0 = 67.27
Ostar = 0.003

mass_density_gcm3 = 9.9e-30
mass_density_Mspc3 = mass_density_gcm3 * (100*3e16)**3 / (1000*2e30)

matter = (mass_density_Mspc3 * Omh2 / (H0*0.01)**2) / M_all
baryons = (mass_density_Mspc3 * Obh2 / (H0*0.01)**2) / M_all
cdm = (mass_density_Mspc3 * Och2 / (H0*0.01)**2) / M_all


## Obs: planets
mplan, ndplan, nplan = np.genfromtxt(pwd + '/../data/planets_obs.txt').T
#rho_star = .0594 # mass density of stars in local volume of planet sample. https://arxiv.org/abs/1807.04592.
#ndplan *= Ostar * mass_density_Mspc3 / rho_star
ax1.plot(mplan, nplan, c='#8C13DA', ls='-', label='Planets')


## Obs: white dwarfs
mwds,ndwds = np.genfromtxt(pwd + '/../data/WD_Number_Density.csv').T
ax1.plot(mwds,ndwds, c='mediumpurple', ls = '-', label = 'White Dwarfs')


## Obs: Neutron Stars
mns,ndns = np.genfromtxt(pwd + '/../data/NS_Number_Density.csv').T
ax1.plot(mns,ndns, c='violet', ls = '-', label = 'Neutron Stars')


## Obs: local group galaxies
mgal_exp, ndgal, _ = np.genfromtxt(pwd + '/../data/galaxies_obs_dwarfGal.txt').T
mgal = 10**mgal_exp

idxs = np.nonzero(ndgal)
mgal_new = mgal[idxs]
ndgal_new = ndgal[idxs]

ax1.plot(mgal_new, ndgal_new, c='#F20483', ls='-', label='Galaxies (local group)')


## Obs: galaxies, SDSS
mgal_exp, ndgal, _ = np.genfromtxt(pwd + '/../data/galaxies_obs_SDSS.txt').T
mgal = 10**mgal_exp

idxs = np.nonzero(ndgal)
mgal_new = mgal[idxs]
ndgal_new = ndgal[idxs]

ax1.plot(mgal_new, ndgal_new, c='#CC2EC7', ls='-', label='Galaxies, SDSS')


## Obs: galaxies, GAMA
mgal_exp, ndgal, _ = np.genfromtxt(pwd + '/../data/galaxies_obs_GAMA.txt').T
mgal = 10**mgal_exp

idxs = np.nonzero(ndgal)
mgal_new = mgal[idxs]
ndgal_new = ndgal[idxs]

ax1.plot(mgal_new, ndgal_new, c='k', ls='-', label='Galaxies, GAMA')


gal_bw = np.genfromtxt(pwd + '/../data/jake_sims_binwidths.txt').T

## Simulations: galaxies -- Illustris TNG300
mgal_tng = np.genfromtxt(pwd + '/../data/illustris/mbins.txt').T

ndgal_tng3 = np.genfromtxt(pwd + '/../data/illustris/dNbydMdV_Mstar_TNG300.txt').T
idxs = np.nonzero(ndgal_tng3)
mgal_tng3 = mgal_tng[idxs]
ndgal_tng3_new = ndgal_tng3[idxs] * gal_bw[idxs]

ax1.plot(mgal_tng3, ndgal_tng3_new, c='#EA5B42', ls='-', label='Galaxies, Illustris TNG300')

ndgal_tng3_vir = np.genfromtxt(pwd + '/../data/illustris/dNbydMdV_Mvir_TNG300.txt').T
idxs = np.nonzero(ndgal_tng3_vir)
mgal_tng3_vir = mgal_tng[idxs]
ndgal_tng3_vir_new = ndgal_tng3_vir[idxs] * gal_bw[idxs]

ax1.plot(mgal_tng3_vir, ndgal_tng3_vir_new, c='#802313', ls='-', label=r'TNG300, M$_{\rm vir}$')

## Illustris TNG100
ndgal_tng1 = np.genfromtxt(pwd + '/../data/illustris/dNbydMdV_Mstar_TNG100.txt').T
idxs = np.nonzero(ndgal_tng1)
mgal_tng1 = mgal_tng[idxs]
ndgal_tng1_new = ndgal_tng1[idxs] * gal_bw[idxs]

ax1.plot(mgal_tng1, ndgal_tng1_new, c='#4284EA', ls='-', label='Galaxies, Illustris TNG100')

ndgal_tng1_vir = np.genfromtxt(pwd + '/../data/illustris/dNbydMdV_Mvir_TNG100.txt').T
idxs = np.nonzero(ndgal_tng1_vir)
mgal_tng1_vir = mgal_tng[idxs]
ndgal_tng1_vir_new = ndgal_tng1_vir[idxs] * gal_bw[idxs]

ax1.plot(mgal_tng1_vir, ndgal_tng1_vir_new, c='#274B83', ls='-', label=r'TNG100, M$_{\rm vir}$')

'''
ndgal_tng1_bar = np.genfromtxt(pwd + '/../data/illustris/dNbydMdV_Mbary_TNG100.txt').T
idxs = np.nonzero(ndgal_tng1_bar)
mgal_tng1_bar = mgal_tng[idxs]
ndgal_tng1_bar_new = ndgal_tng1_bar[idxs]

ax1.plot(mgal_tng1_bar, ndgal_tng1_bar_new, c='#63E8D6', ls='-', label=r'TNG100, M$_{\rm bary}$')
'''


## Simulations: galaxies -- Eagle
ndgal_eag = np.genfromtxt(pwd + '/../data/eagle/dNbydMdV_Mstar_EAGLE').T
idxs = np.nonzero(ndgal_eag)
mgal_eag = mgal_tng[idxs]
ndgal_eag_new = ndgal_eag[idxs] * gal_bw[idxs]

ax1.plot(mgal_eag, ndgal_eag_new, c='#69FF02', ls='-', label='Galaxies, Eagle100')


ndgal_eag_vir = np.genfromtxt(pwd + '/../data/eagle/dNbydMdV_Mvir_EAGLE.txt').T
idxs = np.nonzero(ndgal_eag_vir)
mgal_eag_vir = mgal_tng[idxs]
ndgal_eag_vir_new = ndgal_eag_vir[idxs] * gal_bw[idxs]

ax1.plot(mgal_eag_vir, ndgal_eag_vir_new, c='#3d850a', ls='-', label=r'M$_\mathrm{vir}$, Eagle100')

ndgal_eag25 = np.genfromtxt(pwd + '/../data/eagle/dNbydMdV_Mstar_EAGLE25').T
idxs = np.nonzero(ndgal_eag25)
mgal_eag25 = mgal_tng[idxs]
ndgal_eag25_new = ndgal_eag25[idxs] * gal_bw[idxs]

ax1.plot(mgal_eag25, ndgal_eag25_new, c='#9f6203', ls='-', label='Galaxies, Eagle25')

ndgal_eag25_vir = np.genfromtxt(pwd + '/../data/eagle/dNbydMdV_Mvir_EAGLE25').T
idxs = np.nonzero(ndgal_eag25_vir)
mgal_eag25_vir = mgal_tng[idxs]
ndgal_eag25_vir_new = ndgal_eag25_vir[idxs] * gal_bw[idxs]

ax1.plot(mgal_eag25_vir, ndgal_eag25_vir_new, c='#f99700', ls='-', label=r'M$_\mathrm{vir}$, Eagle25')


m_mag_vir, ndgal_mag_vir = np.genfromtxt(pwd + '/../data/magneticum_range.csv', delimiter=',').T
#ax1.plot(ndgal_mag_vir[:,0], ((ndgal_mag_vir[:,1]*0.23)/ndgal_mag_vir[:,0])/1e18, c='k', ls='-', label=r'M$_\mathrm{vir}$, Magneticum')
ax1.plot(m_mag_vir, ndgal_mag_vir * 0.23 / 1e18, c='k', ls='-', label=r'M$_\mathrm{vir}$, Magneticum')


## Planck cosmology
ax1.plot(M_all, baryons, c='#3498DB', ls='--', label='Baryons')
ax1.plot(M_all, cdm,  c='#2ECC71', ls='--', label='Dark matter')
ax1.plot(M_all, matter, c='#8E44AD', ls=':', label='Baryons + DM')


## Theory: stellar initial mass function
Mbins = np.array([0.01, 0.08, 0.5, 100])
alpha = np.array([0.3, 1.3, 2.3])

Total = Ostar * mass_density_Mspc3

Norms = np.zeros(len(alpha))
Norms[-1] = 1.
for i in range(2):
    Norms[-(i+2)] = Norms[-(i+1)] * Mbins[-(i+2)]**(-alpha[-(i+1)]+alpha[-(i+2)])

Norm = Total / np.sum(Norms * (Mbins[1:]**(-alpha+2) - Mbins[:-1]**(-alpha+2))/(-alpha+2))
Norms *= Norm

imf = np.zeros(2)
for ii in range(3):
    imf = Norms[ii] * alpha[ii] * Mbins[ii:ii+2]**(-(alpha[ii] +1))
    if ii < 2:
        ax1.plot(Mbins[ii:ii+2], imf, c='#54F0F0', ls='-')
    else:
        ax1.plot(Mbins[ii:ii+2], imf, c='#54F0F0', ls='-', label='Stellar IMF')


## Theory: limits
nmin = 1e-32
ns = 2.6e38 / M_all**3
nobs = 6.0953e-81 * M_all**(-1.5)

plt.axhline(nmin, ls='--', c='#F39C12', label='Minimum')
#plt.plot(M_all, ns / M_all, ls='--', c='#CF2419', label='Maximum')


#ax1.text(.2, .95, 'Observations', transform=ax1.transAxes, fontsize=8, color='k')
#ax1.text(.39, .95, 'Simulations', transform=ax1.transAxes, fontsize=8, color='k')
#ax1.text(.66, .95, 'Planck cosmology', transform=ax1.transAxes, fontsize=8, color='k')
#ax1.text(.83, .95, 'Theory', transform=ax1.transAxes, fontsize=8, color='k')
handles, labels = ax1.get_legend_handles_labels()
print('labels',labels)
'''
reorder = [0, 1, 2, 3, 4, 5]
handles = [handles[i] for i in reorder]
labels = [labels[i] for i in reorder]
'''
#labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
plt.legend(handles, labels, loc=[.4,.7], bbox_transform=ax1.transAxes, ncol=3, fontsize=6)
#plt.tight_layout()
plt.show()
plt.savefig(pwd + '/dndv.png')

# TODO: plot total mass of universe (number density of that mass over the size of the universe) and see if it agrees w/ where the 'Minimum' theory line and Baryons+DM line meet
