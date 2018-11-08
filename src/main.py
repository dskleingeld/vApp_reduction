import psf.from_simulated_psf as psf
import disk as d
import plot.fast as plotfast
import plot.slow as plotslow
import numpy as np
from scipy import signal
from hcipy import * 

    #TODO rewrite pipline so params rotation and time are stored next 
    # to the data in a dict
def adi(angular_seperation, time_between_exposures, numb):
    
    #set disk properties
    disk_without_star = d.disk(10, with_star=False, inner_radius=1,
                        outer_radius=3, rotation=135, inclination=70)
    disk_with_star = d.disk(10, with_star=True, inner_radius=1,
                     outer_radius=3, rotation=135, inclination=70)
    
    #process disk without center star
#    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_without_star, angular_seperation)
    plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube_without_star, img_params) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    #process disk with center star
    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_with_star, angular_seperation)
    plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube_with_star, img_params) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    #do adi
    mean = np.mean(img_cube_with_star, axis=0)
    
    plotfast.image(img_cube_with_star-mean)
    
    
if __name__ == "__main__":
    adi(10, 0.7, 10)
