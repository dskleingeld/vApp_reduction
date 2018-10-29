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
import disk
import plot.fast as plotfast
import plot.slow as plotslow

from scipy import signal

if __name__ == "__main__":
    
    disk_properties = disk.properties(1e3, with_star=False,inner_radius=1e2,outer_radius=5e2)
    clean_disk = disk.from_properties(disk_properties, resolution=200)
    
    clean_psf = psf.get_clean()  
    #TODO specler/abberations (load/gen new?)
    #print(clean_psf)
    #print(clean_disk)
    simulated_output = signal.convolve2d(clean_disk,clean_psf)
    
    #print(simulated_output)
    #plotfast.image(clean_disk)

    from matplotlib import pyplot as plt
    plt.clf()
    plt.imshow(simulated_output, interpolation='none', origin = 'lower',
               cmap = plt.get_cmap('afmhot'))
    plt.colorbar(label = 'Relative luminosity')
    plt.title('Intensity profile')
    plt.show()
