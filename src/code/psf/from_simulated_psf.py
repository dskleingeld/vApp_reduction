import numpy as np
from scipy import signal
import astropy.io.fits as fits
import pickle

from multiprocessing import Pool
from tqdm import tqdm
from functools import partial
import os
import glob
import sys

from asdf import AsdfFile

import subprocess
from typing import List, Set, Dict, Tuple, Optional

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
    filepath = os.getcwd().split("vApp_reduction",1)[0]+"vApp_reduction/data/psf_cube_cache/"
    filepath += "psf_cube_"+str(float(fried_parameter))+"_"+str(float(time_between))+"_"+str(int(numb))+".asdf"

    #expand to only demand numb =< numb on disk
    if os.path.exists(filepath):

        tree = AsdfFile.open(filepath, copy_arrays=True).tree
        tree_keys = tree.keys()
        psf_params = sorted(list(filter(lambda key: isinstance(key, float), tree_keys)))
        psf_cube = list(map(lambda param: np.copy(tree[param]), psf_params))
        return psf_cube, psf_params
    else:
        path =  os.getcwd()+"/code/psf/generate_vAPP_cube.py"
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


def conv(args):
    (psf, field) = args
    len_side = int(np.sqrt(psf.shape))

    psf = psf.reshape(len_side, len_side)
    field = field.reshape(len_side, len_side)
    res = signal.convolve2d(psf, field, boundary='symm', mode='same')
    return res


def convolve_cube(psf_cube, field_cube, psf_params, field_params):
    img_params = list(zip(psf_params, field_params))
    cached_results = sorted(glob.glob('../data/convolved_cache/?.params'))
    for params_path in cached_results:
        with open(params_path, "rb") as fp:
            params = pickle.load(fp)
            if params == img_params:
                print("loading old result from disk")
                img_cube = np.load(params_path[:-len('.params')]+'.data.npz')["img_cube"]
                return img_cube, img_params

    img_cube = []
    print("recalculating convolution")

    #print(type(field_cube[0]))
    args = zip(psf_cube,field_cube)
    with Pool(16) as p:
        with tqdm(total=len(img_params)) as pbar:
            for i, img in tqdm(enumerate(p.imap(conv, args))):
                pbar.update()
                img_cube.append(img)


    highest_numb = len(cached_results)
    with open("../data/convolved_cache/"+str(highest_numb)+'.params', "wb") as fp: pickle.dump(img_params, fp)
    np.savez_compressed("../data/convolved_cache/"+str(highest_numb)+'.data.npz', img_cube=img_cube)
    return img_cube, img_params


# test code
def get_clean():
    clean_simulated_psf_path = "SCExAO_vAPP_model.fits"
    with fits.open("../data/"+clean_simulated_psf_path) as hdul:
        # hdul.info()
        return hdul[0].data