import numpy as np
import matplotlib.pyplot as plt #matplotlib 3.0
import matplotlib.colors as colors

from mpl_toolkits.axes_grid1 import make_axes_locatable

def image(data):
    fig, ax = plt.subplots()
    ax.imshow(data)
    plt.show()

def saveImage(data, path, vmin=0.0000001, vmax=None):
    fig, ax = plt.subplots()
    cmap = plt.cm.OrRd
    cmap.set_under(color='white')
    ax.imshow(np.abs(data), interpolation='none', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.savefig(path)

def saveImage_withCb(data, path, log=False, vmin=None, vmax=None, lim=None, labels=None):
    fig, ax = plt.subplots()
    cmap = plt.cm.OrRd
    #cmap = plt.cm.RdBu
    cmap.set_under(color='white')
    
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes("right", size="5%", pad=0.05)
    
    data = np.abs(data)
    if log == False: 
        plt.imshow(data/data.max(), interpolation='none', cmap=cmap, vmin=0.1e-7, vmax=vmax)
    else:
        plt.imshow(data/data.max(), interpolation='none', cmap=cmap, norm=colors.LogNorm())

    if lim != None:
        plt.xlim(lim[0][0],lim[0][1])
        plt.ylim(lim[1][0],lim[1][1])

    #cbar = fig.colorbar(im, cax=cax, orientation="vertical")
    cbar = plt.colorbar()
    cbar.set_label("contrast (brightness relative to brightest spot")

    if labels == None:
        plt.xlabel(r"x position (pixels)")
        plt.ylabel(r"y position (pixels)")
    else:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])   

    fig.savefig(path)
    #plt.show()
