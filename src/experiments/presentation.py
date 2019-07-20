from code.adi import *
from .results import gen_disk_dataset_without_star_perfect_psf, gen_disk_dataset_without_star
import code.plot.fast as plotfast

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors

# time_between_exposures: float = 20
# fried_parameter: float = 18
# field_size: float = 10 
# inner_radius: float = 2
# outer_radius: float = 5
# rotation: float = 120
# inclination: float = 60 
# set_rotation: float = 60
# numb: int = 20

class Params:
    time_between_exposures: float = 20
    fried_parameter: float = 18
    numb: int = 20
    field_size: float = 10 
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    rings = [(0.3,0.5)] #percent of radius of rings and gaps, start stop tuples
    amplification=50

params = Params()

def get_simulated():

    (psf_cube, psf_params) = psf.calc_cube(
        200, fried_parameter=params.fried_parameter, time_between=params.time_between_exposures)

    clean_psf = psf.get_clean()

    length = int(np.sqrt(psf_cube[0].shape[0]))
    psf_cube = [psf.reshape(length,length) for psf in psf_cube]
    (psf_cube, _) = center_cube(psf_cube, ref_img=clean_psf)

    normalised = []
    for psfimg in psf_cube:
        #leakage_max = psfimg[95:105, 95:105].max()
        leakage_max = psfimg.max()
        normalised.append(psfimg/leakage_max)

    return normalised

def get_on_sky():

    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    full_path = script_path+"vApp_reduction/data/"

    hdul = fits.open(full_path+"pbimage_14_36_50.575271241_bg.fits")
    data = hdul[0].data
    hdul.info()

    ref_psf = data[0]

    padded = [np.pad(data[i], ((4+25,4+25),(13,13)), 'constant', constant_values=((0,0),(0,0))) for i in range(200)]
    (aligned, _) = center_cube(padded, ref_img=padded[0])

    #leakage term location:
    #122 -140 x
    #84 - 102 y
    #plotfast.image(aligned[0][84:102, 122:140])

    normalised = []
    for psfimg in aligned:
        #leakage_max = psf[84:102, 122:140].max()
        leakage_max = psfimg.max()
        normalised.append((psfimg/leakage_max))
    
    return normalised

def compare_psfs():
    on_sky_psfs = get_on_sky()
    simulated_psfs = get_simulated()

    #plotfast.image(np.array(on_sky_psfs))
    output_path = get_output_path("presentation")

    fig = plt.figure()
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    ax1=fig.add_subplot(1,2,1)
    ax2=fig.add_subplot(1,2,2)

    ax1.set_xlim([11,101])
    ax1.set_ylim([3,93])
    ax2.set_xlim([47,137])
    ax2.set_ylim([170, 80])

    ax1.axis('off')
    ax2.axis('off')

    ims = []
    for simulated_psf, on_sky_psf in zip(simulated_psfs, on_sky_psfs):
        sim_psf = simulated_psf#[22:125, 10:120]
        ok_sky = np.clip(on_sky_psf, 0.0001, None)#[45:130, 80:165]

        im1 = ax1.imshow(sim_psf, interpolation='none', norm=colors.LogNorm(), animated=True, vmax=0.01)
        im2 = ax2.imshow(ok_sky, interpolation='none', norm=colors.LogNorm(), animated=True, vmin=0.01)
        ims.append([im1,im2])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                    repeat_delay=1000)

    ani.save(output_path+"psf_comp.mpeg", writer="ffmpeg")
    plt.show()

def create_observation():
    numb=20
    (img_cube, _img_params) = gen_disk_dataset(params.time_between_exposures, params.fried_parameter, params.field_size,0,0, 
                                               params.rotation, params.inclination, params.set_rotation, numb, 
                                               rings=params.rings, amplification=params.amplification)
    
    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    return left_psfs

def show_observation():
    left_psfs= create_observation()

    #plotfast.image(np.array(on_sky_psfs))
    output_path = get_output_path("presentation")

    fig = plt.figure()
    fig.subplots_adjust(left=0, bottom=0, right=0, top=0, wspace=None, hspace=None)

    plt.axis('off')

    ims = []
    for left_psf in left_psfs:
        im1 = plt.imshow(left_psf, interpolation='none', norm=colors.LogNorm(), animated=True, vmax=0.0001)
        ims.append([im1])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                    repeat_delay=1000)

    ani.save(output_path+"left_obs.mp4", writer="ffmpeg")
    plt.show()