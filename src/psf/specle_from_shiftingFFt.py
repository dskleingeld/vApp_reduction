from PIL import Image
from scipy.misc import imresize
import numpy as np

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
    Fdata += Fdata * in_specler
    
    out_data = np.fft.ifft2(Fdata).real
    #cant plot the imaginary part so "cast to real"
    return(out_data, in_specler)
