from code.adi import *
import code.plot.slow as plotslow
import os

import matplotlib.pyplot as plt

def run():
    
    time_between_exposures: float = 20
    fried_parameter: float = 18
    field_size: float = 10 
    inner_radius: float = 2
    outer_radius: float = 5
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    numb: int = 20
    
    output_path = get_output_path("miscellaneous")

    ################################ disk image #########################

    # set disk properties
    disk_with_star = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
        outer_radius=outer_radius, rotation=45, inclination=60, rings = [(0.2,0.5)])

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        1, disk_with_star, set_rotation)
    #plotfast.image(disk_cube[0])
    plotslow.saveImage(disk_cube[0], output_path+"disk_45_60")

    # set disk properties
    disk_with_star = d.disk(field_size=field_size, with_star=False, inner_radius=2.2,
        outer_radius=2.3, rotation=45, inclination=80, rings = [(1.0,1.3),(0.3,0.8)] )

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        1, disk_with_star, set_rotation)
    #plotfast.image(disk_cube[0])
    plotslow.saveImage(disk_cube[0], output_path+"disk_45_10_22_23")

    ############################### psf difference ##########################

    (psf_cube, psf_params) = psf.calc_cube(
        50, fried_parameter=fried_parameter, time_between=time_between_exposures)

    clean_psf = psf.get_clean()

    length = int(np.sqrt(psf_cube[0].shape[0]))
    psf_cube = [psf.reshape(length,length) for psf in psf_cube]
    (psf_cube, _) = center_cube(psf_cube, ref_img=clean_psf)

    normalised = []
    for psfimg in psf_cube:
        #leakage_max = psfimg[95:105, 95:105].max()
        leakage_max = psfimg.max()
        normalised.append(psfimg/leakage_max)

    #plt.imshow(psf_cube[0])
    #plt.show()
    plotfast.image(np.array(normalised))

    difference1 = normalised[0]-normalised[1]
    difference2 = normalised[0]-normalised[9]
    difference3 = normalised[0]-normalised[49]

    plotslow.saveImage_withCb(difference1, output_path+"psf_diff_007", norm=False)
    plotslow.saveImage_withCb(difference2, output_path+"psf_diff_070", norm=False)
    plotslow.saveImage_withCb(difference3, output_path+"psf_diff_140", norm=False)

    #plotfast.image(np.array([difference1,difference3, difference2]))

def on_sky():
    ############################### on sky psf difference ######################

    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    full_path = script_path+"vApp_reduction/data/"

    hdul = fits.open(full_path+"pbimage_14_36_50.575271241_bg.fits")
    data = hdul[0].data
    hdul.info()

    ref_psf = data[0]

    padded = [np.pad(data[i], ((4+25,4+25),(13,13)), 'constant', constant_values=((0,0),(0,0))) for i in range(50)]
    (aligned, _) = center_cube(padded, ref_img=padded[0])

    #leakage term location:
    #122 -140 x
    #84 - 102 y
    #plotfast.image(aligned[0][84:102, 122:140])

    normalised = []
    for psfimg in aligned:
        #leakage_max = psf[84:102, 122:140].max()
        leakage_max = psfimg.max()
        normalised.append(psfimg/leakage_max)
    
    # still contains a few bad shot, not a problem for our purpose
    plotfast.image(np.array(normalised))

    difference1 = normalised[0]-normalised[1]
    difference2 = normalised[0]-normalised[9]
    difference3 = normalised[0]-normalised[49]

    difference1 = np.rot90(difference1[15:-75, 40:-50])
    difference2 = np.rot90(difference2)[20:205, :175]
    difference3 = np.rot90(difference3)[20:205, :175]

    output_path = get_output_path("miscellaneous")
    plotslow.saveImage_withCb(difference1, output_path+"on_sky_psf_diff_007", norm=False)
    plotslow.saveImage_withCb(difference2, output_path+"on_sky_psf_diff_070", norm=False)
    plotslow.saveImage_withCb(difference3, output_path+"on_sky_psf_diff_140", norm=False)



def run_loyt():
    from hcipy import make_pupil_grid, make_focal_grid, FraunhoferPropagator, circular_aperture, evaluate_supersampled, imshow_field, imsave_field, Field, LyotCoronagraph, Wavefront
    import numpy as np
    import matplotlib.pyplot as plt

    pupil_grid = make_pupil_grid(256)
    focal_grid = make_focal_grid(pupil_grid, 8, 32)
    prop = FraunhoferPropagator(pupil_grid, focal_grid)

    aperture = circular_aperture(1)
    aperture = evaluate_supersampled(aperture, pupil_grid, 8)

    mask = 1 - circular_aperture(3)(focal_grid)
    stop = circular_aperture(0.7)(pupil_grid)
    coro = LyotCoronagraph(pupil_grid, mask, stop)

    wf = Wavefront(aperture)
    lyot = coro(wf)

    img = prop(lyot)
    img_ref = prop(wf)

    output_path = get_output_path("miscellaneous")

    fig = plt.figure()
    imshow_field(np.log10(img.power / img_ref.power.max()), vmin=-6, vmax=0)
    plt.xlim(-25,25)
    plt.ylim(-25,25)
    cbar = plt.colorbar()
    cbar.set_label(r"$^{10}\log(contrast)$")
    plt.ylabel(r"$\lambda/D$")
    plt.xlabel(r"$\lambda/D$")
    fig.savefig(output_path+"lyot_psf")

    fig = plt.figure()
    imshow_field(np.log10(img_ref.power / img_ref.power.max()), vmin=-6, vmax=0)
    plt.xlim(-25,25)
    plt.ylim(-25,25)
    cbar = plt.colorbar()
    cbar.set_label(r"$^{10}\log(contrast)$")
    plt.ylabel(r"$\lambda/D$")
    plt.xlabel(r"$\lambda/D$")
    fig.savefig(output_path+"normal_psf")

def clean_vapp():
    import numpy as np
    import matplotlib.pyplot as plt 

    from hcipy import read_fits, make_pupil_grid, make_focal_grid, FraunhoferPropagator, circular_aperture, evaluate_supersampled, imshow_field, imsave_field, Field, LyotCoronagraph, Wavefront

    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    full_path = script_path+"vApp_reduction/data/"
    amplitude_file = full_path+'SCExAO_vAPP_amplitude_resampled.fits'
    phase_file     = full_path+'SCExAO_vAPP_phase_resampled.fits'

    # loading the files required for generating the vAPP. 
    amplitude_temp = read_fits(amplitude_file)
    phase_temp     = read_fits(phase_file)

    # number of pixels along one axis in the pupil
    Npix = amplitude_temp.shape[0]

    # generating the grids 
    pupil_grid = make_pupil_grid(Npix)
    focal_grid = make_focal_grid(pupil_grid, 4, 25)

    # Mapping from pupil plane to focal plane
    propagator = FraunhoferPropagator(pupil_grid, focal_grid)

    # converting the amplitude and phase to fields 
    amplitude = Field(amplitude_temp.ravel(), pupil_grid)
    phase     = Field(phase_temp.ravel(), pupil_grid)

    # the wavefront for the three PSFs 
    pupil_wf_PSF_1 = Wavefront(amplitude * np.exp(1j * phase)) # coronagraphic PSF 1
    pupil_wf_PSF_2 = Wavefront(amplitude * np.exp(-1j * phase)) # coronagraphic PSF 2
    pupil_wf_PSF_3 = Wavefront(amplitude) # leakage

    # Propagating them to the focal plane 
    focal_wf_PSF_1 = propagator(pupil_wf_PSF_1)
    focal_wf_PSF_2 = propagator(pupil_wf_PSF_2)
    focal_wf_PSF_3 = propagator(pupil_wf_PSF_3)

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

    fig = plt.figure()
    imshow_field(np.log10(total_PSF / total_PSF.max()), vmin=-5, vmax=0)

    cbar = plt.colorbar()
    cbar.set_label(r"$^{10}\log(contrast)$")
    plt.ylabel(r"$\lambda/D$")
    plt.xlabel(r"$\lambda/D$")

    plt.show()
    output_path = get_output_path("miscellaneous")
    fig.savefig(output_path+"clean_vapp")
    
    fig = plt.figure()
    imshow_field(np.log10(total_PSF / total_PSF.max()), vmin=-5, vmax=0)

    bbox_props = dict(boxstyle="circle,pad=0.3", fill=False, alpha=1, fc=None, ec="red", lw=5)
    plt.text(10.3, 10.7, " ", ha="center", va="center", rotation=45,
            size=110,
            bbox=bbox_props)
    plt.text(-10.3, -10.7, " ", ha="center", va="center", rotation=45,
            size=110,
            bbox=bbox_props)
    bbox_props = dict(boxstyle="circle,pad=0.3", fill=False, alpha=1, fc=None, ec="white", lw=5)
    plt.text(0, 0, " ", ha="center", va="center", rotation=45,
            size=55,
            bbox=bbox_props)
    plt.text(8, -15, " ", ha="center", va="center", rotation=45,
            size=55,
            bbox=bbox_props)
    plt.text(-8, 15, " ", ha="center", va="center", rotation=45,
            size=55,
            bbox=bbox_props)


    cbar = plt.colorbar()
    cbar.set_label(r"$^{10}\log(contrast)$")
    plt.ylabel(r"$\lambda/D$")
    plt.xlabel(r"$\lambda/D$")

    plt.show()
    output_path = get_output_path("miscellaneous")
    fig.savefig(output_path+"clean_vapp_annotated")

def plot_sub_psfs():
    
    
    def gen_adi_star_controlset(time_between_exposures: float, fried_parameter: float, 
        set_rotation: float, numb: int):
        
        angular_seperation = set_rotation / numb

        star = np.zeros((200, 200))
        star[int(star.shape[0] / 2), int(star.shape[1] / 2)] = 1
        field_cube = [star.copy() for i in range(0,numb)]
        field_params = [[angular_seperation * i] for i in range(0, numb)]

        (psf_cube, psf_params) = psf.calc_cube(
            numb, fried_parameter=fried_parameter, time_between=time_between_exposures)
        (img_cube, img_params) = psf.convolve_cube(psf_cube, field_cube, psf_params, field_params)

        return (img_cube, img_params)
    
    time_between_exposures: float = 0.7
    fried_parameter: float = 4
    set_rotation: float = 60
    numb: int = 20
    
    output_path = get_output_path("miscellaneous")

    (img_cube, img_params) = gen_adi_star_controlset(time_between_exposures,fried_parameter, set_rotation, numb)
    write_metadata(output_path+"meta", time_between_exposures=time_between_exposures, fried_parameter=fried_parameter, 
        set_rotation=set_rotation, numb=numb)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    #(left, right) = find_sub_psf_location_from_cube(img_cube)
    ##alternatively use coords from perfect psf
    (left, right) = find_sub_psf_location(clean_psf)
    
    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)
        
    plotslow.saveImage(img_cube[0], output_path+"full_aligned", vmax = 0.001)
    plotslow.saveImage(right_psfs[0], output_path+"right_subpsf", vmax = 0.001)
    plotslow.saveImage(left_psfs[0], output_path+"left_subpsf", vmax = 0.001)
