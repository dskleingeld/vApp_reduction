import numpy as np
import matplotlib.pyplot as plt #matplotlib 3.0

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