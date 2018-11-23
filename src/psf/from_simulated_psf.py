import numpy as np
from scipy import signal
import astropy.io.fits as fits
import skimage.draw as sk
import itertools
import pickle

from multiprocess import Pool
from tqdm import tqdm
from functools import partial
import os
import glob


from asdf import AsdfFile, Stream
import asdf

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

def calc_cube(numb, fried_parameter = 4, time_between = 0.7):
    filepath = "psf_cube_"+str(fried_parameter)+"_"+str(time_between)+"_"+str(numb)+".asdf"
    
    #expand to only demand numb =< numb on disk
    if os.path.exists(filepath):
        
        tree = AsdfFile.open(filepath, copy_arrays=True).tree
        tree_keys = tree.keys()
        psf_params = sorted(list(filter(lambda key: isinstance(key, float), tree_keys)))
        psf_cube = list(map(lambda param: np.copy(tree[param]), psf_params))
        return psf_cube, psf_params
    else:
        path =  os.getcwd()+"/psf/generate_vAPP_cube.py"
        params = [str(fried_parameter), str(time_between), str(numb)]
        cmd = ["python3", path, *params]
        print(cmd)
        myrun(cmd)
        
        tree = AsdfFile.open(filepath).tree
        tree_keys = tree.keys()
        psf_params = sorted(list(filter(lambda key: isinstance(key, float), tree_keys)))
        psf_cube = list(map(lambda param: tree[param], psf_params))
        
        return psf_cube, psf_params
 
def conv(psf_cube, disk_cube):
    len_side = int(np.sqrt(psf_cube.shape))
    psf_cube = psf_cube.reshape(len_side,len_side)
    disk_cube = disk_cube.reshape(len_side,len_side)
    res = signal.convolve2d(psf_cube, disk_cube, boundary='symm', mode='same')

    return res

## note: input comes from async `calc_psf`
def update(pbar, img_cube, res):
    img_cube.append(res)
    pbar.update()

def convolve(psf_cube, disk_cube, psf_params, disk_params):
    img_params = list(zip(psf_params, disk_params))
    cached_results = sorted(glob.glob('?.params'))
    for params_path in cached_results:
        with open(params_path, "rb") as fp:
            params = pickle.load(fp)
            if params == img_params:
                print("loading old result from disk")
                img_cube = np.load(params_path[:-len('.params')]+'.data.npz')["img_cube"]
                return img_cube, img_params 
                
    img_cube = []
    print("recalculating convolution")
    pbar = tqdm(total=len(img_params))
    pool = Pool(processes=16)
    callback = partial(update, pbar, img_cube)
    for psf, disk in zip(psf_cube, disk_cube):
        pool.apply_async(conv, args=(psf, disk), callback=callback)
    pool.close()
    pool.join()
    pbar.close()
    
    highest_numb = len(cached_results)
    with open(str(highest_numb)+'.params', "wb") as fp: pickle.dump(img_params, fp)
    np.savez_compressed(str(highest_numb)+'.data.npz', img_cube=img_cube)
    
    return img_cube, img_params

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
