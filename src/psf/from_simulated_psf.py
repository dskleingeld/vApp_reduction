import numpy as np
import astropy.io.fits as fits
import skimage.draw as sk

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

def createSpecle():
    
    A = normalise(circle((1000,1000), radius=0.05) )
    B = np.fft.fftshift(np.fft.fft2(A))
    B = np.abs(B)
    specle = np.real(B)
    
    return A,specle;
