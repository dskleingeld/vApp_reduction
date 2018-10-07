import numpy as np
import astropy.io.fits as fits

#test code
def get_clean():
    clean_simulated_psf_path = "SCExAO_vAPP_model.fits"
    with fits.open("../data/"+clean_simulated_psf_path) as hdul:
        #hdul.info()
        return hdul[0].data

def get_on_sky():
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"    
    with fits.open("../data/"+on_sky_set) as hdul:
        #hdul.info()
        return [ hdul[0].data[0], hdul[0].data[1] ]

def get_on_sky(length):
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"    
    with fits.open("../data/"+on_sky_set) as hdul:
        #hdul.info()
        hdulist = []
        for i in range(length):
            hdulist.append(hdul[0].data[i])
        return hdulist

def normalise(array):
    mins = np.min(array)
    maxs = np.max(array)
    rng = maxs - mins
    return (array-mins)/(maxs - mins)

def sin2d(x, y):
    return np.sin(y * x)

def box(shape):
    A = np.empty(shape,dtype=complex)
    
    for x in np.arange(0, shape[0]):
        for y in np.arange(0, shape[1]):
            if (x > 80) and (x < 120) and (y > 80) and (y< 120):
                A[x,y] = 1j+1
            else:
                A[x,y] = 0
    return A

def sine(shape):
    A = np.empty(shape,dtype=complex)
    
    for x in np.arange(0, shape[0]):
        for y in np.arange(0, shape[1]):
            A[x,y] = (1j+1)*np.sin(x)
    return A

from PIL import Image
from scipy.misc import imresize
def load_black_and_white(shape, path):    
    image_file = Image.open(path) # open colour image
    image_file = image_file.convert('1') # convert image to black and white
    image_shape = image_file.size
    np_frame = np.array(image_file.getdata()).reshape(image_shape)
    
    A = imresize(np_frame, shape)
    return normalise(A)

def field(shape, func):
    print(shape[0])
    x = np.linspace(-10, 10, shape[0])
    y = np.linspace(-10, 10, shape[1])
    result = func(x[:,None], y[None,:])
    print("shape {0}".format(shape))
    return normalise(result)

def apply_specles(in_data, path):
    Fdata = np.fft.fft2(in_data)
    
    #specler = field(Fdata.shape, sin2d)
    #specler = box(Fdata.shape)*0.8
    #specler = sine(Fdata.shape)*0.8
    specler = load_black_and_white(Fdata.shape, path)
    Fdata = Fdata * specler
    
    out_data = np.fft.ifft2(Fdata).real
    #cant plot the imaginary part so "cast to real"
    return(out_data, specler)
    #print(out_data)
