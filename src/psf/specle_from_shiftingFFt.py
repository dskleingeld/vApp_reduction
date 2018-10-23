from PIL import Image
from scipy.misc import imresize
import numpy as np
import skimage.draw as sk
from skimage.filters import gaussian

def normalise(array):
    mins = np.min(array)
    maxs = np.max(array)
    rng = maxs - mins
    return (array-mins)/(maxs - mins)

def load_black_and_white(shape, path):    
    image_file = Image.open(path) # open colour image
    image_file = image_file.convert('L') # convert image to black and white
    image_shape = image_file.size
    np_frame = np.array(image_file.getdata()).reshape(image_shape)
    
    A = imresize(np_frame, shape)
    return normalise(A)

def apply_specles(in_data, in_specler):
    Fdata = np.fft.fft2(in_data)
    
    #specler = field(Fdata.shape, sin2d)
    #specler = box(Fdata.shape)*0.8
    #specler = sine(Fdata.shape)*0.8
    Fdata = Fdata #* in_specler
    
    out_data = np.fft.ifft2(Fdata).real
    #cant plot the imaginary part so "cast to real"
    return(out_data, in_specler)

def apply_specles_from_path(in_data, path):
    Fdata = np.fft.fft2(in_data)
    
    #specler = field(Fdata.shape, sin2d)
    #specler = box(Fdata.shape)*0.8
    specler = load_black_and_white(in_data.shape, path)
    Fdata = Fdata * specler
    
    out_data = np.fft.ifft2(Fdata).real
    #cant plot the imaginary part so "cast to real"
    return(out_data, specler)

def add_image(in_data, path):
    #specler = field(Fdata.shape, sin2d)
    #specler = box(Fdata.shape)*0.8
    specler = load_black_and_white(in_data.shape, path)
    out_data += in_data * specler
    #out_data = in_data * specler
    
    return(out_data, specler)    

#coord is coordinate relative to left bottem corner
# specle needs to have 4x the number of pixels then the source
# TODO: deal with uneven input
def place_random_circles(source: np.ndarray):
    radius = 0.05 #radius of background to sample to determine brightness 
    source = np.fft.fft2(source)
    
    source_middle_x = source.shape[0]//2
    source_middle_y = source.shape[1]//2
    
    index = 0
    numb_of_specles = 50
    y = np.random.normal(loc=source_middle_y, scale=source_middle_y,size=(numb_of_specles) )
    x = np.random.normal(loc=source_middle_x, scale=source_middle_x,size=(numb_of_specles) )
    coords = np.stack((x, y), axis=-1)
    
    A = np.zeros(source.shape,dtype=float)
    for coord in coords:
        y_pos = int(coord[0])
        x_pos = int(coord[1])
        if( y_pos <= 0-radius or y_pos >= source.shape[1]+radius-1):
            continue
        elif( x_pos <= 0-radius or x_pos >= source.shape[0]+radius-1):
            continue
        
        rr, cc = sk.circle(x_pos, y_pos, radius*min(source_middle_x,source_middle_y), shape=source.shape )
        A[rr,cc] = 1
     
    source *= A
    
    return np.fft.ifft2(source).real, A

def place_circle_grid(source: np.ndarray, radius=4, spacing=2, blur=0):
    numb_in_x = int(source.shape[0] / (radius*2+spacing) ) 
    numb_in_y = int(source.shape[1] / (radius*2+spacing) )
    
    x = np.linspace(radius, source.shape[0]+radius, numb_in_x, endpoint=False, dtype=int)
    y = np.linspace(radius, source.shape[1]+radius, numb_in_y, endpoint=False, dtype=int)
    xv, yv = np.meshgrid(x, y)

    A = np.zeros(source.shape,dtype=float)   
    for (x, y) in zip(xv.flat, yv.flat):
        rr, cc = sk.circle(x, y, radius, shape=source.shape )
        A[rr,cc] = 1    

    A = gaussian(A,sigma=blur)
    source = np.fft.fft2(source)
    source *= A
    source = np.fft.ifft2(source).real
    
    return source, A
