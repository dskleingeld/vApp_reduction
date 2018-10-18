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
import plot.slow as plotslow
import glob

if __name__ == "__main__":
    
    # #process, 
    # clean_sim = psf.get_clean()
    # #on_sky =psf.get_on_sky()
	
    # sims = []
    # speclers = []
    
    # paths = []
    
    
    # for (i, path) in enumerate(glob.glob("../specler_images/*") ):
        # (simulated, specler) = psf.apply_specles(clean_sim, path)
        # sims.append(simulated)
        # speclers.append(specler)
        # paths.append(path)
    
    # on_skies = psf.get_on_sky(len(sims))
    
    # titles = [list(a) for a in zip([""] * len(paths),[""] * len(paths), paths)]
    
    #plot
    #A, specle = psf.createSpecle()
    #plotfast.image(A)
    #plotfast.image(specle)
    
    #import numpy as np
    #image = np.zeros((300,300))
    
    #random_numbers = np.random.normal(loc=0.0, scale=30.0,size=(100,2) )
    
    #psf.placeSpecles(image, specle, [(10,10),(-20,30),(30,-30)])
    #plotslow.image(image)
    #plotfast.image(image)
    
    #plotfast.compare([sims,on_skies,speclers])

    import numpy as np
    def modify_psf(clean_sim):
        sims = []
        speclers = []
        paths = []
        
        for (i, path) in enumerate(glob.glob("../specler_images/*.png")
        +glob.glob("../specler_images/*.jpg")
        +glob.glob("../specler_images/*.gif") ):
            (simulated, specler) = psf.apply_specles_from_path(clean_sim, path)
            sims.append(simulated)
            speclers.append(specler)
            paths.append(path)
        
        on_skies = psf.get_on_sky(len(sims))
        
        titles = [list(a) for a in zip([""] * len(paths),[""] * len(paths), paths)]
        
        #plot
        plotfast.compare([sims,on_skies,speclers],titles=titles)

    def roll_psf_fft(clean_sim):
        image = psf.load_black_and_white(clean_sim.shape, "../specler_images/two.gif")
        sims = []
        speclers = []
        for i in range(1,100):
            image = np.roll(image, 3)
            (simulated, specler) = psf.apply_specles(clean_sim, image)
            sims.append(simulated)
            speclers.append(specler)
        on_skies = psf.get_on_sky(len(sims))
        plotfast.compare([sims,on_skies,speclers])

    def place_specles(image):
        image_withSpecles = psf.add_specles(image_clean)
        #plotfast.compare([[image_clean,image_withSpecles]]  )    
        plotfast.image(image_withSpecles)
        #plotslow.image(image_withSpecles)

    def compare():
        image_clean = psf.get_clean()      
        sims = []       
        for i in range(1,100):
            image_withSpecles = psf.add_specles(image_clean)
            sims.append(image_withSpecles)
    
        on_skies = psf.get_on_sky(len(sims))
        plotfast.image(sims[0])
        plotfast.compare([sims,on_skies])
    
    def change_phase():
        spectrum = psf.get_spectrum(image_clean)
        phase = psf.phase_from_spectrum(spectrum)
        magnitude = psf.magnitude_from_spectrum(spectrum)
        # spectrum = psf.spectrum_from_phase(phase, magnitude)
        # org = psf.org_from_spectrum(spectrum)
        
        image_clean = psf.get_clean()      
        sims = []       
        for i in range(1,10):
            modded_phase = phase*psf.circle(phase.shape, radius=1/i)
            spectrum = psf.spectrum_from_phase(modded_phase, magnitude)
            sim = psf.org_from_spectrum(spectrum)
            sims.append(sim)
        
        on_skies = psf.get_on_sky(len(sims))
        plotfast.image(sims[0])
        plotfast.compare([sims,on_skies])   
    
    def add_to_phase():
        spectrum = psf.get_spectrum(image_clean)
        phase = psf.phase_from_spectrum(spectrum)
        magnitude = psf.magnitude_from_spectrum(spectrum)
        image_clean = psf.get_clean()      
        speclers = []
        sims = []       
        for (i, path) in enumerate(glob.glob("../specler_images/*.png")
        +glob.glob("../specler_images/*.jpg")
        +glob.glob("../specler_images/*.gif") ):
            modded_phase, specler = psf.add_image(phase, path)
            spectrum = psf.spectrum_from_phase(modded_phase, magnitude)
            sim = psf.org_from_spectrum(spectrum)
            sims.append(sim)
            speclers.append(specler)
        
        on_skies = psf.get_on_sky(len(sims))
        plotfast.image(sims[0])
        plotfast.compare([sims,on_skies])     
    
    image_clean = psf.get_clean()  
    def toplot(funct_args, modifiers_list):
        one, two = psf.place_circle_grid(funct_args,radius=modifiers_list[0], spacing=modifiers_list[1])
        return [one,two]

    plotfast.plotfunct(toplot, image_clean, [1,1])
    #compare()
    #image_clean = psf.get_clean()  
    
    #spectrum = psf.get_spectrum(image_clean)
    #phase = psf.phase_from_spectrum(spectrum)
    #plotfast.image(phase);
    
    #roll_psf_fft(image_clean)
    #modify_psf(image_clean)
    #image_withSpecles = place_specles(image_clean)    
    
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
    
