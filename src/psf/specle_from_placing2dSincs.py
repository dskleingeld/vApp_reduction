import numpy as np
import astropy.io.fits as fits
import skimage.draw as sk

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

def createSpecle(size=5):
    
    A = normalise(circle((1000,1000), radius=1./size) )
    B = np.fft.fftshift(np.fft.fft2(A))
    B = np.abs(B)
    specle = (np.real(B))
    specle = specle*specle
    specle = normalise(specle)
    
    return specle;

#coord is coordinate relative to left bottem corner
def get_local_intensity(source: np.ndarray, coord, radius=5):
    
    rr, cc = sk.circle(coord[0], coord[1], radius, shape=source.shape)
    #intensity = np.min(source[rr,cc])
    #intensity = np.mean(source[rr,cc])
    #intensity = np.max(source[rr,cc])
    
    #TODO should not be nessesairy fix!
    if source[rr,cc].size < 0:
        return 0
    
    intensity = np.median(source[rr,cc])
    return intensity


#coord is coordinate relative to left bottem corner
# specle needs to have 4x the number of pixels then the source
# TODO: deal with uneven input
def place_specles(org_source: np.ndarray, specle: np.ndarray, coords, intensity_offset):
    source = org_source.copy()
    radius = 2. #radius of background to sample to determine brightness 
    
    specle_middle_x = specle.shape[0]//2
    specle_middle_y = specle.shape[1]//2
    
    source_middle_x = source.shape[0]//2
    source_middle_y = source.shape[1]//2
    
    index = 0
    for coord in coords:
        y_pos = int(coord[0])
        x_pos = int(coord[1])
        if( y_pos <= 0-radius or y_pos >= source.shape[1]+radius-1):
            continue
        elif( x_pos <= 0-radius or x_pos >= source.shape[0]+radius-1):
            continue
        
        specle_view_begin_y = specle_middle_y - y_pos
        specle_view_begin_x = specle_middle_x - x_pos
        specle_view_end_y = specle_middle_y + 2*source_middle_y - y_pos
        specle_view_end_x = specle_middle_x + 2*source_middle_x - x_pos
     
        specle_subview = specle[specle_view_begin_x:specle_view_end_x,specle_view_begin_y:specle_view_end_y]
     
        intensity = get_local_intensity(org_source, coord, radius) *1e-0#* intensity_offset[index]
        source += (specle_subview*intensity)
        index+=1
    
    return source

def add_specles(image):
    #for now hardcode locations, in free time try writing a rust 
    #funct to find this automagically
    numb_of_specles = 400 #per source
    for (locx,locy) in [(58,58),(141,141)]:        
        y = np.random.normal(loc=locy, scale=180.0,size=(numb_of_specles) )
        x = np.random.normal(loc=locx, scale=180.0,size=(numb_of_specles) )
        intensity_offset = np.clip(np.random.normal(1, scale=1.0, size=(numb_of_specles)),0,2)

        coords = np.stack((x, y), axis=-1)
        image = place_specles(image, createSpecle(size=3), coords, intensity_offset)
 
        #image[locx,locy] = 10 #used to verify center location
    
    return image
