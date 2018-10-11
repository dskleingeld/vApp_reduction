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
    specle = normalise(np.real(B))
    
    return A, specle;

#coord is coordinate relative to left bottem corner
def get_local_intensity(source: np.ndarray, coord):
    
    A = np.zeros((source[0],source[1]),dtype=float)
    
    rr, cc = sk.circle(coord[0], coord[1], radius )
    A[rr,cc] = 1

    return np.minimum(source*A)


#coord is coordinate relative to left bottem corner
# specle needs to have 4x the number of pixels then the source
# TODO: deal with uneven input
def place_specles(source_: np.ndarray, specle: np.ndarray, coords, intensity):
    source = source_.copy()
    
    specle_middle_x = specle.shape[0]//2
    specle_middle_y = specle.shape[1]//2
    
    source_middle_x = source.shape[0]//2
    source_middle_y = source.shape[1]//2
    
    index = 0
    for coord in coords:
        y_pos = int(coord[0])
        x_pos = int(coord[1])
        
        specle_view_begin_y = specle_middle_y - y_pos
        specle_view_begin_x = specle_middle_x - x_pos
        specle_view_end_y = specle_middle_y + 2*source_middle_y - y_pos
        specle_view_end_x = specle_middle_x + 2*source_middle_x - x_pos
     
        specle_subview = specle[specle_view_begin_x:specle_view_end_x,specle_view_begin_y:specle_view_end_y]
        
        source += (specle_subview*intensity[index])
        index+=1
    
    return source

def add_specles(image):
    #for now hardcode locations, in free time try writing a rust 
    #funct to find this automagically
    #for (x,y) in [(-50,-55),(28,28)]:
    for (x,y) in [(100,30)]:        
        y = np.random.normal(loc=y, scale=30.0,size=(60) )
        x = np.random.normal(loc=x, scale=30.0,size=(60) )
        coords = np.stack((x, y), axis=-1)
        #intensity = np.full(image.shape, 5e-2)
        intensity = np.full(image.shape, 5e-3)
        
        image = place_specles(image, createSpecle(size=2)[1], coords, intensity)
    return image
