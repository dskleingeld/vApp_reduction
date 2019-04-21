import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
from tqdm import tqdm

import os
import sys

from hcipy import read_fits, make_pupil_grid, make_focal_grid, SpectralNoiseFactoryFFT, make_standard_multilayer_atmosphere, AtmosphericModel, Field, Wavefront, imshow_field, kolmogorov_psd, FraunhoferPropagator
from asdf import AsdfFile, Stream

def calc_psf(t):
    atmospheric_model.t = t # sec
    # applying atmosphere and then propagating them to the focal plane
    focal_wf_PSF_1 = prop(atmospheric_model(pupil_wf_PSF_1))
    focal_wf_PSF_2 = prop(atmospheric_model(pupil_wf_PSF_2))
    focal_wf_PSF_3 = prop(atmospheric_model(pupil_wf_PSF_3))

    # setting the total power in the images
    focal_wf_PSF_1.total_power = 1
    focal_wf_PSF_2.total_power = 1
    focal_wf_PSF_3.total_power = 1

    # the strenght of the leakage term
    leakage = 0.02

    # getting the power and scaling with leakage
    PSF_1_pwr = focal_wf_PSF_1.power * (1 - leakage / 2)
    PSF_2_pwr = focal_wf_PSF_2.power * (1 - leakage / 2)
    PSF_3_pwr = focal_wf_PSF_3.power * leakage

    # generating the total PSF of the vAPP
    total_PSF = PSF_1_pwr + PSF_2_pwr + PSF_3_pwr

    # normalizing to sum = 1
    total_PSF /= np.sum(total_PSF)

    return (t, total_PSF)

## note: input comes from async `calc_psf`
def update(args):
    time = args[0]
    psf = args[1]
    psf_cube[time] = psf
    pbar.update()

script_path = os.path.realpath(__file__)
amplitude_file = script_path.split("vApp_reduction",1)[0]+"vApp_reduction/data/SCExAO_vAPP_amplitude_resampled.fits"
phase_file     = script_path.split("vApp_reduction",1)[0]+"vApp_reduction/data/SCExAO_vAPP_phase_resampled.fits"

#get paramaters from files
params = sys.argv
if len(params) == 4:
    path, fried_parameter, time_between, numb = params
    fried_parameter = float(fried_parameter)
    time_between = float(time_between)
    numb = int(numb)
else:
    fried_parameter = 4 # meter //increased from 0.2 to reduce atmos effects
    time_between = 0.7
    numb = 10

print("generating: "+str(numb)+" psfs with:\n  fried parameter: "+str(fried_parameter)+"\n  sample time: "+str(time_between))

D_tel = 8.2 # meter
wavelength = 1e-6 # meter
oversampling = 8

# loading the files required for generating the vAPP.
amplitude_temp = read_fits(amplitude_file)
phase_temp     = read_fits(phase_file)

# number of pixels along one axis in the pupil
Npix = amplitude_temp.shape[0]

# generating the grids
pupil_grid = make_pupil_grid(Npix, D_tel)
focal_grid = make_focal_grid(pupil_grid, 4, 25, wavelength=wavelength)

#kolmogorov: verdeling voor sterkte special freq
spectral_noise_factory = SpectralNoiseFactoryFFT(kolmogorov_psd, pupil_grid, oversampling)
turbulence_layers = make_standard_multilayer_atmosphere(fried_parameter=fried_parameter, wavelength=wavelength)
# create phase screen
atmospheric_model = AtmosphericModel(spectral_noise_factory, turbulence_layers)

# Mapping from pupil plane to focal plane
prop = FraunhoferPropagator(pupil_grid, focal_grid)

# converting the amplitude and phase to fields
amplitude = Field(amplitude_temp.ravel(), pupil_grid)
phase     = Field(phase_temp.ravel(), pupil_grid)

# the wavefront for the three PSFs
pupil_wf_PSF_1 = Wavefront(amplitude * np.exp(1j * phase), wavelength) # coronagraphic PSF 1
pupil_wf_PSF_2 = Wavefront(amplitude * np.exp(-1j * phase), wavelength) # coronagraphic PSF 2
pupil_wf_PSF_3 = Wavefront(amplitude, wavelength) # leakage

psf_cube = {}
times = np.linspace(0,time_between,numb)
pbar = tqdm(total=len(times))
#https://github.com/tqdm/tqdm/issues/484
if __name__ == '__main__':

    pool = Pool(processes=16)
    for time in times:
        pool.apply_async(calc_psf, args=(time,), callback=update)
    pool.close()
    pool.join()
    pbar.close()


    filepath = script_path.split("vApp_reduction",1)[0]+"vApp_reduction/data/psf_cube_cache/"
    filepath += "psf_cube_"+str(fried_parameter)+"_"+str(time_between)+"_"+str(numb)+".asdf"
    target = AsdfFile(psf_cube)
    target.write_to(filepath, all_array_compression='zlib')
    print("saved psf_cube to: "+filepath)
