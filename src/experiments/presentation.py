from code.adi import *
import code.plot.fast as plotfast

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors

time_between_exposures: float = 0.7
fried_parameter: float = 4
field_size: float = 10 
inner_radius: float = 2
outer_radius: float = 5
rotation: float = 120
inclination: float = 60 
set_rotation: float = 60
numb: int = 20


def get_simulated():

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

    return normalised

def get_on_sky():

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
        normalised.append((psfimg/leakage_max))
    
    return normalised

def compare_psfs():
    on_sky_psfs = get_on_sky()
    simulated_psfs = get_simulated()

    #plotfast.image(np.array(on_sky_psfs))
    output_path = get_output_path("presentation")

    fig = plt.figure()
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

        im1 = ax1.imshow(sim_psf, interpolation='none', norm=colors.LogNorm(), animated=True)
        im2 = ax2.imshow(ok_sky, interpolation='none', norm=colors.LogNorm(), animated=True, vmin=0.001)
        ims.append([im1,im2])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                    repeat_delay=1000)

    ani.save(output_path+"psf_comp.mpeg", writer="ffmpeg")
    plt.show()