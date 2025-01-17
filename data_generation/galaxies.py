import sys

import numpy as np

from astropy.cosmology import FlatLambdaCDM

from astropy.io import fits

# Cosmological values from Planck, as used by IllustrisTNG
Omega_m = 0.3089
h = 0.6774
cosmo = FlatLambdaCDM(H0=h*100.0, Om0=Omega_m)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        datasets = [*sys.argv[1:]]
    else:
        datasets = ["SDSS", "GAMA", "dwarfGal"]
else:
    datasets = []

def get_data(dataset="SDSS"):
    if dataset == "SDSS":
        # Columns in table are tot_mass, tot_mass_width, z, z_err, objID, specObjID, petroR50_r, R_hlr (for 202842 objects)
        sdssdr7 = np.genfromtxt("../data/sdssdr7_mass_radius.csv", delimiter=',', skip_header=1)

        #SDSS data
        tot_mass = sdssdr7[:, 0] # log(M) with M in M_sun
        # tot_mass_width = sdssdr7[:, 1]
        z = sdssdr7[:, 2] # redshift
        # z_err = sdssdr7[:, 3]
        # petroR50_r = sdssdr7[:, 6]
        # R_hlr = sdssdr7[:, 7]
    elif dataset == "GAMA":
        # gamaData = fits.open('../data/GAMA.fits')[1].data
        # tot_mass = gamaData['logmstar'] # log(M) with M in M_sun
        gamaData = fits.open('../data/GAMA_massradii.fits')[1].data
        tot_mass = gamaData['logmstar'] # log(M) with M in M_sun
        z = gamaData['Z'] # redshift

        mass_limit = np.where((tot_mass > 5.9) * (z < 0.08))
        tot_mass = tot_mass[mass_limit]
        z = z[mass_limit]
    elif dataset == "dwarfGal":
        dg = fits.open('../data/dwarfGal.fits')[1].data
        tot_mass = np.log10(1e6 * dg["Mass"]) # log(M) with M in M_sun
        distance = dg["D_MW_"]/1e3 # distance in Mpc
        # radius = dg["R1"] # in arcmin

        val_mass = np.where(np.isfinite(tot_mass))

        tot_mass = tot_mass[val_mass]
        distance = distance[val_mass]
        # radius = radius[val_mass]
        z = None

    if dataset in ["SDSS", "GAMA"]:
        distance = cosmo.comoving_distance(z).to("Mpc").value

    return (tot_mass, distance, z)

# Bin data

def get_dist_bins(distance, z=None, dataset="SDSS"):
    _, dist_bin_edges = np.histogram(distance, bins=50)
    # _, dist_bin_edges, _ = ax_dist.hist(distance, bins=50, color='k', histtype="step")

    # dist_bins = [(-np.inf, np.inf), (-np.inf, 100), (100, 200), (200, 300), (300, 400)]

    dist_bins = [(-np.inf, np.inf)]
    z_bins = [(-np.inf, np.inf)]
    labels = ["All"]

    if z is not None:
        z_ip = np.linspace(0, 1.1*np.max(z), 1e6)

    if dataset == "SDSS":
        dbedges = np.array([0, 50, 100, 150, 200, 250, 275, 300, 320, 350])
    elif dataset == "GAMA":
        dbedges = np.arange(0, 400, 50)
    elif dataset == "dwarfGal":
        dbedges = np.zeros(1)
    
    if z is not None:
        zedges = np.interp(dbedges, cosmo.comoving_distance(z_ip), z_ip)

    for di in range(dbedges.size - 1):
        dist_bins.append((dbedges[di], dbedges[di+1]))
        if z is not None:
            z_bins.append((zedges[di], zedges[di+1]))

        if dbedges[di] == 0:
            labels.append(r"$D<{:.0f} \, \mathrm{{Mpc}}$".format(dbedges[di+1]))
        elif dbedges[di+1] > np.max(distance):
            labels.append(r"$D>{:.0f} \, \mathrm{{Mpc}}$".format(dbedges[di]))
        else:
            labels.append(r"${:.0f} < D \leq {:.0f} \, \mathrm{{Mpc}}$".format(dbedges[di], dbedges[di+1]))
    
    return (dist_bin_edges, dist_bins, z_bins, labels)

def get_mass_bins(dataset="SDSS"):
    if dataset in ["SDSS", "GAMA"]:
        # N_bins = int(1e4)
        # M_bin_edges = np.arange(np.round(min_mass, 1)-0.1, np.round(max_mass, 1)+0.1, 0.1)
        # M_bin_edges = np.log10(np.logspace(np.round(min_mass, 1)-0.1, np.round(max_mass, 1)+0.1, 1e4))
        M_bin_edges = np.linspace(5, np.log10(5e15), 200)
        # M_bin_edges_Ill = np.loadtxt("../data/illustris/mbins.txt")

        M_bin_centers = 0.5*(M_bin_edges[:-1] + M_bin_edges[1:])
    elif dataset == "dwarfGal":
        M_bin_edges = np.linspace(2.5, 9.5, 5)

        M_bin_centers = 0.5*(M_bin_edges[:-1] + M_bin_edges[1:])


    return (M_bin_edges, M_bin_centers)

def get_dndmdv(tot_mass, M_bin_edges, distance, dist_bin, z_bin, z=None, dataset="SDSS"):
    dist_mask = (distance > dist_bin[0]) * (distance <= dist_bin[1])
    argmax_distance = np.argmax(distance[dist_mask])
    max_distance = distance[dist_mask][argmax_distance]
    
    if z is not None:
        z_max = z[dist_mask][argmax_distance]

    N, _ = np.histogram(tot_mass[dist_mask], bins=M_bin_edges)

    N_err = np.sqrt(N)

    # Divide by the width of the mass bins (NB: now using bin width in log(M)!)
    dNdM = N/(M_bin_edges[1:]-M_bin_edges[:-1])
    dNdM_err = N_err/(M_bin_edges[1:]-M_bin_edges[:-1])

    if dataset == "SDSS":
        sky_fraction = 8032.0/(4.0*np.pi*(180.0/np.pi)**2) #8032.0 square degrees for SDSS
    elif dataset == "GAMA":
        sky_fraction = 296.158/(4.0*np.pi*(180.0/np.pi)**2)
    elif dataset == "dwarfGal":
        sky_fraction = 1.0
        # Use a volume of 3 Mpc
        max_distance = 3.0

        # Adjust volume to fix the resulting stellar density to the universal value
        omega_stellar = 3e-3
        M_MW = 6.08e10 # Licquia & Newman (2015)
        M_M31 = 10.3e10 # Sick et al. (2014)
        M_tot = np.sum(10**tot_mass[dist_mask]) + M_MW + M_M31

        V_tot = M_tot/(omega_stellar*cosmo.critical_density0.to("M_sun/Mpc^3").value) # effective volume in Mpc^3

        max_distance = (V_tot / (4.0/3.0 * np.pi))**(1.0/3.0) # effective radius in Mpc

    if np.isneginf(dist_bin[0]) and np.isposinf(dist_bin[1]):
        if z is None:
            dV = 4.0/3.0 * np.pi * (max_distance * 1e6)**3
        else:
            # dV = 4.0/3.0 * np.pi * (max_distance * 1e6)**3
            dV = cosmo.comoving_volume(z_max).to("pc^3").value
    else:
        assert not (np.isneginf(dist_bin[0]) or np.isposinf(dist_bin[1]))
        # dV = 4.0/3.0 * np.pi * ((np.min([dist_bin[1], max_distance]) * 1e6)**3 - (dist_bin[0] * 1e6)**3)
        dV = (cosmo.comoving_volume(np.min([z_bin[1], z_max]))-cosmo.comoving_volume(z_bin[0])).to("pc^3").value

    dNdV = N/(dV*sky_fraction)
    dNdV_err = N_err/(dV*sky_fraction)

    dNdMdV = dNdM/(dV*sky_fraction)
    dNdMdV_err = dNdM_err/(dV*sky_fraction)

    return (dNdM, dNdM_err, dNdV, dNdV_err, dNdMdV, dNdMdV_err)



for dataset in datasets:
    tot_mass, distance, z = get_data(dataset=dataset)

    # plt.hist(tot_mass, bins=50)

    min_mass = np.min(tot_mass)
    max_mass = np.max(tot_mass)
    # print("Mass range:", min_mass, max_mass)

    dist_bin_edges, dist_bins, z_bins, labels = get_dist_bins(distance, z=z, dataset=dataset)

    M_bin_edges, M_bin_centers = get_mass_bins(dataset=dataset)

    if dataset == "dwarfGal":
        dNdM, dNdM_err, dNdV, dNdV_err, dNdMdV, dNdMdV_err = get_dndmdv(tot_mass, M_bin_edges, distance,
                                                z=z, dist_bin=(-np.inf, np.inf), z_bin=(-np.inf, np.inf), dataset=dataset)
    elif dataset in ["SDSS", "GAMA"]:
        dNdV_final = np.tile(-np.inf, M_bin_centers.size)
        dNdMdV_final = np.tile(-np.inf, M_bin_centers.size)

        for dbi, dist_bin in enumerate(dist_bins[1:]):
            dNdM, dNdM_err, dNdV, dNdV_err, dNdMdV, dNdMdV_err = get_dndmdv(tot_mass, M_bin_edges, distance,
                                                                            dist_bin, z_bins[1+dbi], z=z, dataset=dataset)

            dNdV_final = np.where(dNdV > dNdV_final, dNdV, dNdV_final)
            dNdMdV_final = np.where(dNdMdV > dNdMdV_final, dNdMdV, dNdMdV_final)

    data = np.array([M_bin_centers, (M_bin_edges[1:]-M_bin_edges[:-1]), dNdV, dNdMdV])

    footerText = "/Galaxies (SDSS)/'#2ecc71'/'-'/"
    np.savetxt("../data/galaxies_obs_" + dataset + ".txt", data.T,
                fmt='%1.3e \t', header="M (M_s) \t dlog(M/M_s) \t dN/dV (pc^-3) \t dN/dMdV (M_s^-1 pc^-3)", footer=footerText)