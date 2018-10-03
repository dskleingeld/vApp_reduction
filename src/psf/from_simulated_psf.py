import numpy as np
import astropy.io.fits as fits

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


def sin2d(x, y):
    return np.sin(y * x)
    
def field(shape, func):
    x = np.linspace(-10, 10, shape[0])
    y = np.linspace(-10, 10, shape[1])
    result = func(x[:,None], y[None,:])
    print("shape"+result.shape)
    return result

def apply_specles(in_data):
    Fdata = np.fft.fft2(in_data)
    
    
    field = (Fdata.shape, sin2d)
    Fdata = Fdata * field
    
    out_data = np.fft.ifft2(Fdata).real
    return(out_data, field)
    #print(out_data)
