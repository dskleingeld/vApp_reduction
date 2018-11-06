# general program layout, needs more thought mainly:
# - how does this scape up for running multiple runs with diff paramaters?
# - how can an auto analasis/quantifying procedure be included?
# - future multithreading?

    #get disk
        #set disk/object properties, get obj/disk class
    
    #process, 
        #load/create psf and get its dimensions
    
    #rdi
        #generate single complete psf's, this code lives in the psf modele:
            #generate the (disk) non spreaded image
            #convolve the disk with the psf 
        #generate proc
        
        
        #return both processed and generated input(s)?
    
    #adi
        #generate multiple complete psf's, this code lives in the psf modele:
            #generate the (disk) non spreaded image
            #convolve the disk with the psf 
        #generate processed image
        #return both processed and generated input(s)? 
    
    #plot
        #(optional) matplotlib for report printing
        #something faster and better for experimenting

import psf.from_simulated_psf as psf
import disk as d
import plot.fast as plotfast
import plot.slow as plotslow
from scipy import signal
from hcipy import * 

    #https://github.com/spacetelescope/asdf
def adi(angular_seperation, time_between_exposures, numb):
    
    #set disk properties
    clean_disk = d.disk(10, with_star=False, inner_radius=1,
                 outer_radius=3, rotation=135, inclination=70)
    
    #create disk cube
    #disk_cube = d.gen_cube(clean_disk, angular_seperation, numb)
    
    #lazily create psf cube
    psf_cube = psf.calc_cube() #fix in ultra ugly way
    
    #lazily convolve signals
    image_cube = process_clean(psf_cube, disk_cude)
    
    #do adi
    #plotfast.image(clean_disk)
    
if __name__ == "__main__":
    adi(10, 0.7, 10)
