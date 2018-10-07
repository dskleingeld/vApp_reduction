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
import plot.fast as plotfast
import glob

if __name__ == "__main__":
    
    #process, 
    clean_sim = psf.get_clean()
    #on_sky =psf.get_on_sky()
	
    sims = []
    speclers = []
    
    paths = []
    
    
    for (i, path) in enumerate(glob.glob("../specler_images/*") ):
        (simulated, specler) = psf.apply_specles(clean_sim, path)
        sims.append(simulated)
        speclers.append(specler)
        paths.append(path)
    
    on_skies = psf.get_on_sky(len(sims))
    
    titles = [list(a) for a in zip([""] * len(paths),[""] * len(paths), paths)]
    
    #plot
    plotfast.compare([sims,on_skies,speclers],titles=titles)
    
    
    
    
    
    
    ########################TESTING###################
    
    if False:
        import numpy as np
        
        def func(x, y):
            return np.sin(y * x)
        
        x = np.linspace(-10, 10, 200)
        y = np.linspace(-10, 10, 200)
        result = func(x[:,None], y[None,:])
        plotfast.image(on_sky[0])
    
    
    ###################################################
    # properties = disk.properties(radius=5)
    # body = disk.from_properties()
    
