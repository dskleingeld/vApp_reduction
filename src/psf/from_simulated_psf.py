import numpy as np
import astropy.io.fits as fits
import skimage.draw as sk
import itertools
from multiprocess import Pool
import os

from asdf import AsdfFile, Stream

#from .specle_from_shiftingFFt import *
#from .specle_from_placing2dSincs import *

import subprocess
def myrun(cmd):
    """from http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
        print(line),
        if line == '' and p.poll() != None:
            break
    return ''.join(stdout)

def calc_cube(fried_parameter = 4, time_between = 0.7, numb = 30):
    filepath = "psf_cube_"+str(fried_parameter)+"_"+str(time_between)+"_"+str(numb)+".asdf"
    if os.path.exists(filepath): 
        return AsdfFile.open(filepath)
    else:
        path =  os.getcwd()+"/psf/generate_vAPP_cube.py"
        params = [str(fried_parameter), str(time_between), str(numb)]
        cmd = ["python3", path, *params]
        print(cmd)
        myrun(cmd)
        return AsdfFile.open(filepath)

def process_clean(psf_cube, image_cube):
    with Pool(processes=16) as pool:
        return pool.map(signal.convolve2d, [psf_cube, disk_cube])

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
