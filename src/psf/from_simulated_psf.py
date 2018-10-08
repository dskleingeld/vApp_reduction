import numpy as np
import astropy.io.fits as fits
import skimage.draw as sk
import itertools

#test code
def get_clean():
    clean_simulated_psf_path = "SCExAO_vAPP_model.fits"
    with fits.open("../data/"+clean_simulated_psf_path) as hdul:
        #hdul.info()
        return hdul[0].data

def get_on_sky():
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"    
    with fits.open("../data/"+on_sky_set) as hdul:
        #hdul.info()
        return [ hdul[0].data[0], hdul[0].data[1] ]

def get_on_sky(length):
    on_sky_set = "pbimage_14_36_50.575271241_bg.fits"    
    with fits.open("../data/"+on_sky_set) as hdul:
        #hdul.info()
        hdulist = []
        for i in range(length):
            hdulist.append(hdul[0].data[i])
        return hdulist

def normalise(array):
    mins = np.min(array)
    maxs = np.max(array)
    rng = maxs - mins
    return (array-mins)/(maxs - mins)

def circle(shape, radius=0.5):
    A = np.zeros(shape,dtype=float)
    
    rr, cc = sk.circle(shape[0]/2, shape[1]/2, radius*min(shape[0]/2,shape[1]/2) )
    A[rr,cc] = 1
    
    return A

def field(shape, func):
    print(shape[0])
    x = np.linspace(-10, 10, shape[0])
    y = np.linspace(-10, 10, shape[1])
    result = func(x[:,None], y[None,:])
    print("shape {0}".format(shape))
    return normalise(result)

def apply_specles(in_data, path):
    Fdata = np.fft.fft2(in_data)
    
    specler = field(Fdata.shape, circle)
    Fdata = Fdata * specler
    
    out_data = np.fft.ifft2(Fdata).real
    #cant plot the imaginary part so "cast to real"
    return(out_data, specler)
    #print(out_data)

########################################################################

def createSpecle(size=5):
    
    A = normalise(circle((1000,1000), radius=1./size) )
    B = np.fft.fftshift(np.fft.fft2(A))
    B = np.abs(B)
    specle = normalise(np.real(B))
    
    return A, specle;

# specle needs to have 4x the number of pixels then the source
# to do: deal with uneven input
def place_specles(source_: np.ndarray, specle: np.ndarray, coords, intensity):
    source = source_.copy()
    
    specle_middle_x = specle.shape[0]//2
    specle_middle_y = specle.shape[1]//2
    
    source_middle_x = source.shape[0]//2
    source_middle_y = source.shape[1]//2
    
    index = 0
    for coord in coords:
        x_pos = int(coord[0])
        y_pos = int(coord[1])
        
        specle_view_begin_x = specle_middle_x - source_middle_x +x_pos
        specle_view_begin_y = specle_middle_y - source_middle_y +y_pos
        specle_view_end_x = specle_middle_x + source_middle_x + x_pos
        specle_view_end_y = specle_middle_y + source_middle_y + y_pos
     
        specle_subview = specle[specle_view_begin_x:specle_view_end_x,specle_view_begin_y:specle_view_end_y]
        source += (specle_subview*intensity[index])
        index+=1
    
    return source

def add_specles(image):
    #for now hardcode locations, in free time try writing a rust 
    #funct to find this automagically
    for (x,y) in [(-40,-40),(25,25)]:
        
        y = np.random.normal(loc=y, scale=30.0,size=(10) )
        x = np.random.normal(loc=x, scale=30.0,size=(10) )
        coords = np.stack((x, y), axis=-1)
        intensity = np.full(image.shape, 1e-2)
        
        image = place_specles(image, createSpecle(size=2)[1], coords, intensity)
    return image
