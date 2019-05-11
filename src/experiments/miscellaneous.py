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

    output_path = get_output_path("miscellaneous")
    plotslow.saveImage(difference1, output_path+"on_sky_psf_diff_007")
    plotslow.saveImage(difference2, output_path+"on_sky_psf_diff_070")
    plotslow.saveImage(difference3, output_path+"on_sky_psf_diff_140")



def run_loyt():
    from hcipy import make_pupil_grid, make_focal_grid, FraunhoferPropagator, circular_aperture, evaluate_supersampled, imshow_field, imsave_field, Field, LyotCoronagraph, Wavefront
    import numpy as np
    import matplotlib.pyplot as plt
    import skimage.draw as sk

    def circle(shape, radius=0.5):
        A = np.zeros(shape,dtype=float)
        
        rr, cc = sk.circle(shape[0]/2, shape[1]/2, radius*min(shape[0]/2,shape[1]/2) )
        A[rr,cc] = 1
        
        return A

    pupil_grid = make_pupil_grid(1024)
    focal_grid = make_focal_grid(pupil_grid, 8, 32)
    prop = FraunhoferPropagator(pupil_grid, focal_grid)

    aperture = circular_aperture(1)
    aperture = evaluate_supersampled(aperture, pupil_grid, 8)

    mask = Field(circle((1024,1024), radius=0.5).ravel(), pupil_grid)
    stop = Field((1-circle((1024,1024), radius=0.5)).ravel(), focal_grid)
    coro = LyotCoronagraph(pupil_grid, mask, stop)

    wf = Wavefront(aperture)
    lyot = coro(wf)

    img = prop(lyot)
    img_ref = prop(wf)


    output_path = get_output_path("lyot")

    fig = plt.figure()
    imshow_field(np.log10(img.intensity / img_ref.intensity.max()), vmin=-12)
    plt.colorbar()
    fig.savefig(output_path+"lyot_psf")

    fig = plt.figure()
    imshow_field(np.log10(img_ref.intensity / img_ref.intensity.max()), vmin=-12)
    plt.colorbar()
    fig.savefig(output_path+"normal_psf")