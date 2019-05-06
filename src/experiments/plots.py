from code.adi import *
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
    
    output_path = get_output_path("normal_disk")

    ################################ disk image #########################

    # set disk properties
    disk_with_star = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
        outer_radius=outer_radius, rotation=rotation, inclination=inclination)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        1, disk_with_star, set_rotation)
    plotfast.image(disk_cube[0])

    ############################### psf difference ##########################

    (psf_cube, psf_params) = psf.calc_cube(
        2, fried_parameter=fried_parameter, time_between=time_between_exposures)
    difference = psf_cube[0]-psf_cube[1]
    length = int(np.sqrt(difference.shape[0]))
    difference = difference.reshape(length, length)

    plotfast.image(difference)

    ############################### on sky psf difference ######################

    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    full_path = script_path+"vApp_reduction/data/"

    hdul = fits.open(full_path+"pbimage_14_36_50.575271241_bg.fits")
    data = hdul[0].data

    

    plotfast.image(data)
