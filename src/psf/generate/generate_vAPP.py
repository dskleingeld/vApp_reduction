import numpy as np
import matplotlib.pyplot as plt 

from hcipy import * 

amplitude_file = 'SCExAO_vAPP_amplitude_resampled.fits'
phase_file     = 'SCExAO_vAPP_phase_resampled.fits'

fried_parameter = 0.2 # meter
outer_scale = 20 # meter
velocity = 10 # meter/sec

D_tel = 8.2 # meter
wavelength = 1e-6 # meter

# loading the files required for generating the vAPP. 
amplitude_temp = read_fits(amplitude_file)
phase_temp     = read_fits(phase_file)

# number of pixels along one axis in the pupil
Npix = amplitude_temp.shape[0]

# generating the grids 
pupil_grid = make_pupil_grid(Npix, D_tel)
focal_grid = make_focal_grid(pupil_grid, 4, 25, wavelength=wavelength)

# building atmospheric layers
Cn_squared = Cn_squared_from_fried_parameter(fried_parameter, 500e-9)
layer = InfiniteAtmosphericLayer(pupil_grid, Cn_squared, outer_scale, velocity)
layer.t = 0.1 # sec

# Mapping from pupil plane to focal plane
prop = FraunhoferPropagator(pupil_grid, focal_grid)

# converting the amplitude and phase to fields 
amplitude = Field(amplitude_temp.ravel(), pupil_grid)
phase     = Field(phase_temp.ravel(), pupil_grid)

# the wavefront for the three PSFs 
pupil_wf_PSF_1 = Wavefront(amplitude * np.exp(1j * phase), wavelength) # coronagraphic PSF 1
pupil_wf_PSF_2 = Wavefront(amplitude * np.exp(-1j * phase), wavelength) # coronagraphic PSF 2
pupil_wf_PSF_3 = Wavefront(amplitude, wavelength) # leakage

focal_wf_PSF_1 = prop(layer(pupil_wf_PSF_1))
focal_wf_PSF_2 = prop(layer(pupil_wf_PSF_2))
focal_wf_PSF_3 = prop(layer(pupil_wf_PSF_3))

## Propagating them to the focal plane 
#focal_wf_PSF_1 = prop(pupil_wf_PSF_1)
#focal_wf_PSF_2 = prop(pupil_wf_PSF_2)
#focal_wf_PSF_3 = prop(pupil_wf_PSF_3)

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

plt.figure()
imshow_field(np.log10(total_PSF / total_PSF.max()), vmin=-5)
plt.colorbar()

plt.show()
