import numpy as np
from scipy import signal
import astropy.io.fits as fits
import pickle

from multiprocess import Pool
from tqdm import tqdm
from functools import partial
import os
import glob
import sys

from asdf import AsdfFile

import subprocess


def myrun(cmd):
    """from http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
    """
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
        print(line),
        if line == '' and p.poll() != None:
            break
    return ''.join(stdout)


def calc_cube(numb, fried_parameter = 4, time_between = 0.7):
    filepath = os.getcwd().split("vApp_reduction",1)[0]+"vApp_reduction/data/"
    filepath += "psf_cube_"+str(float(fried_parameter))+"_"+str(float(time_between))+"_"+str(int(numb))+".asdf"
    
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
        cmd = [sys.executable, path, *params]
        print("please run: ")
        print(' '.join(cmd))
        input("Press Enter to continue...")
        
        tree = AsdfFile.open(filepath).tree
        tree_keys = tree.keys()
        psf_params = sorted(list(filter(lambda key: isinstance(key, float), tree_keys)))
        psf_cube = list(map(lambda param: tree[param], psf_params))
        
        return psf_cube, psf_params
 
    
def conv(psf, field):
    len_side = int(np.sqrt(psf.shape))
    psf = psf.reshape(len_side, len_side)
    field = field.reshape(len_side, len_side)
    res = signal.convolve2d(psf, field, boundary='symm', mode='same')
    print("convolving")
    return res


## note: input comes from async `calc_psf`
def update(pbar, img_cube, res):
    img_cube.append(res)
    pbar.update()
    print("appending")
    
    
def convolve(psf_cube, field_cube, psf_params, field_params):
    img_params = list(zip(psf_params, field_params))
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
    
    for psf, field in zip(psf_cube, field_cube):
        print("test")
        pool.apply_async(conv, args=(psf, field), callback=callback)
    pool.close()
    pool.join()
    pbar.close()
    
    highest_numb = len(cached_results)
    with open(str(highest_numb)+'.params', "wb") as fp: pickle.dump(img_params, fp)
    np.savez_compressed(str(highest_numb)+'.data.npz', img_cube=img_cube)
    print(img_cube)
    return img_cube, img_params


# test code
def get_clean():
    clean_simulated_psf_path = "SCExAO_vAPP_model.fits"
    with fits.open("../data/"+clean_simulated_psf_path) as hdul:
        # hdul.info()
        return hdul[0].data


def get_on_sky():
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"
    with fits.open("../data/"+on_sky_set) as hdul:
        # hdul.info()
        return [hdul[0].data[0], hdul[0].data[1]]


def get_on_sky(length):
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"
    with fits.open("../data/"+on_sky_set) as hdul:
        # hdul.info()
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
    a = np.real(np.fft.fft2(spectrum))
    return a
