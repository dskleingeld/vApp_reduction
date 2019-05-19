import numpy as np
import matplotlib.pyplot as plt #matplotlib 3.0
from mpl_toolkits.axes_grid1 import make_axes_locatable

def image(data):
    fig, ax = plt.subplots()
    ax.imshow(data)
    plt.show()

def saveImage(data, path):
    fig, ax = plt.subplots()
    cmap = plt.cm.OrRd
    cmap.set_under(color='white')    
    ax.imshow(np.abs(data), interpolation='none', cmap=cmap, vmin=0.0000001)
    plt.savefig(path)

def saveImage_withCb(data, path, vmax):
    fig, ax = plt.subplots()
    cmap = plt.cm.OrRd
    cmap.set_under(color='white')
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    im = ax.imshow(np.abs(data), interpolation='none', cmap=cmap, vmin=0.0000001, vmax=vmax)
    fig.colorbar(im, cax=cax, orientation="vertical")
    plt.savefig(path)
