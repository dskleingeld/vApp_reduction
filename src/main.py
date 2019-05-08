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
import os
import glob
from scipy import signal

def get_output_path(output_dir: str):
    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    full_path = script_path+"vApp_reduction/plots/"+output_dir

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    cached_results = glob.glob(full_path+'/*.txt')
    output_path = full_path+"/"+str(len(cached_results))+"_"
    return output_path

if __name__ == "__main__":

    image_clean = psf.get_clean()  
    def toplot(funct_args, modifiers_list):
        one, two = psf.place_circle_grid(funct_args,radius=modifiers_list[0], spacing=modifiers_list[1], blur=modifiers_list[2], roll_x=modifiers_list[3], intensity=modifiers_list[4])
        return [one,two]

    plotfast.plotfunct(toplot, image_clean, [16,3, 1.5, -1750, 0.3], [1,1,1,1,1])
    
    psf1, _ = psf.place_circle_grid(image_clean,radius=16, spacing=3, blur=1.5, roll_x=-1750, intensity=0.3)
    psf2, _ = psf.place_circle_grid(image_clean,radius=16, spacing=3, blur=1.5, roll_x=-1740, intensity=0.3)

    psf3, _ = psf.place_circle_grid(image_clean,radius=16, spacing=3, blur=1.5, roll_x=-1750, intensity=0.3)
    psf4, _ = psf.place_circle_grid(image_clean,radius=16, spacing=3, blur=1.5, roll_x=-1745, intensity=0.3)


    difference1 = psf1-psf2
    difference2 = psf3-psf4

    output_path = get_output_path("old_psf_changing")
    plotslow.saveImage(difference1, output_path+"old_psf_diff1")
    plotslow.saveImage(difference2, output_path+"old_psf_diff2")