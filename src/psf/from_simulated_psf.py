import numpy as np
import astropy.io.fits as fits
import skimage.draw as sk
import itertools

from .specle_from_shiftingFFt import *
from .specle_from_placing2dSincs import *

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

def get_spectrum(clean):
    z = np.fft.fft2(clean)
    z = np.fft.fftshift(z)
    return z

def phase_from_spectrum(spectrum):
    phase = np.arctan2(np.imag(spectrum), np.real(spectrum))
    return phase

def magnitude_from_spectrum(spectrum):
    real = np.abs(spectrum)    
    return real

def spectrum_from_phase(phase, magnitude):
    real = magnitude * np.cos(phase)
    imag = magnitude * np.sin(phase)
    return real + imag


def org_from_spectrum(spectrum):
    spectrum = np.fft.ifftshift(spectrum)
    a = np.real(np.fft.fft2(spectrum) )
    return a
