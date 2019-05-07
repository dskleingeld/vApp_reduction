from code.adi import *
import code.plot.slow as plotslow
import os

def run():
    
    time_between_exposures: float = 0.7
    fried_parameter: float = 4
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
        outer_radius=outer_radius, rotation=45, inclination=60)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        1, disk_with_star, set_rotation)
    #plotfast.image(disk_cube[0])
    plotslow.saveImage(disk_cube[0], output_path+"disk_45_60")

    # set disk properties
    disk_with_star = d.disk(field_size=field_size, with_star=False, inner_radius=2.2,
        outer_radius=2.3, rotation=45, inclination=80)

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

    difference1 = psf_cube[0]-psf_cube[1]
    difference2 = psf_cube[0]-psf_cube[9]
    difference3 = psf_cube[0]-psf_cube[49]

    plotslow.saveImage(difference1, output_path+"psf_diff_007")
    plotslow.saveImage(difference2, output_path+"psf_diff_070")
    plotslow.saveImage(difference3, output_path+"psf_diff_140")

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
    for psf in aligned:
        leakage_max = psf[84:102, 122:140].max()
        normalised.append(psf/leakage_max)
    
    # still contains a few bad shot, not a problem for our purpose
    #plotfast.image(np.array(normalised))

    difference1 = normalised[0]-normalised[1]
    difference2 = normalised[0]-normalised[9]
    difference3 = normalised[0]-normalised[49]

    plotslow.saveImage(difference1, normalised+"on_sky_psf_diff_007")
    plotslow.saveImage(difference2, normalised+"on_sky_psf_diff_070")
    plotslow.saveImage(difference3, normalised+"on_sky_psf_diff_140")
