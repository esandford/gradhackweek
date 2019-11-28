import matplotlib as mpl
import numpy as np

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

def plot_all(ax, fns, cuts, cs, lss, labs, pwrs):
    for i in range(len(fns)):
        print('plotting', fns[i])
        bc, dndv, dndvdlm = load_data(fns[i])
        if pwrs[i]:
            bc = 10**bc
        plot_phys(ax, bc, dndv, cuts[i], cs[i], lss[i], labs[i])
        #plot_phys(ax, bc, dndvdlm, cuts[i], cs[i], lss[i], labs[i])

def load_data(fn):
    try:
        bin_center, bin_width, dn_dv, dn_dv_dlogm = np.genfromtxt(fn).T
    except ValueError as e:
        bin_center, dn_dv, dn_dv_dlogm = np.genfromtxt(fn).T
    idxs = np.nonzero(dn_dv)
    # TODO: use this: idxs = np.nonzero(dn_dv_dlogm)
    bin_center = bin_center[idxs]
    dn_dv = dn_dv[idxs]
    dn_dv_dlogm = dn_dv_dlogm[idxs]
    return bin_center, dn_dv, dn_dv_dlogm

def plot_phys(ax, m, nd, cut, c, ls, label):
    if cut > 0: ax.plot(m, nd, c=c, ls=ls, alpha=0.3)
    ax.plot(m[m > cut], nd[m > cut], c=c, ls=ls, label=label)
