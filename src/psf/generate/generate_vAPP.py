import numpy as np
import matplotlib.pyplot as plt 

from hcipy import * 

amplitude_file = 'SCExAO_vAPP_amplitude_resampled.fits'
phase_file     = 'SCExAO_vAPP_phase_resampled.fits'

fried_parameter = 4 # meter //increased from 0.2 to reduce atmos effects

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

# building atmospheric layers
#Cn_squared = Cn_squared_from_fried_parameter(fried_parameter, 500e-9)
#layer = InfiniteAtmosphericLayer(pupil_grid, Cn_squared, outer_scale, velocity)

spectral_noise_factory = SpectralNoiseFactoryFFT(kolmogorov_psd, pupil_grid, oversampling)
turbulence_layers = make_standard_multilayer_atmosphere(fried_parameter=fried_parameter, wavelength=wavelength)
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


times = np.linspace(0,0.7,200)
mw = GifWriter('adaptive_optics2.gif', 10)
fig = plt.figure()
for t in times:
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
    

    imshow_field(np.log10(total_PSF / total_PSF.max()), vmin=-5)
    mw.add_frame(fig=fig)
    plt.clf()
#    imshow_field(np.log10(total_PSF / total_PSF.max()), vmin=-5)

#    plt.draw()
#    plt.pause(0.00001)

#times = np.linspace(0,0.7,200)

#for t in times:
#    atmospheric_model.t = t
#    wf2 = atmospheric_model(wf)

#    sci_img = prop(wf2).intensity
#    wf3 = microlens_array(wf2)
#    wfs_img = sh_prop(wf3).intensity

#    #imshow_field(wf3.phase)
#    #plt.colorbar()
#    #plt.show()

#    plt.clf()
#    plt.subplot(2,2,1)
#    imshow_field(np.log10(sci_img / sci_img.max()), vmin=-5)
#    plt.subplot(2,2,2)
#    imshow_field(wfs_img / wfs_img.max())
#    plt.subplot(2,2,3)
#    imshow_field(wf2.phase * aperture(pupil_grid), vmin=-np.pi, vmax=np.pi, cmap='RdBu')
#    plt.draw()
#    plt.pause(0.00001)
#    #mw.add_frame()
#mw.close()


