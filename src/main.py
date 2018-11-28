import psf.from_simulated_psf as psf
import disk as d
import plot.fast as plotfast
import plot.slow as plotslow
import numpy as np
from scipy import signal, ndimage
import skimage.draw as sk
from hcipy import * 
from scipy.stats import multivariate_normal

#radius numb between 0 and 1
def find_sub_psf_location(img):
    #prepare image by cutting off one of the psf's
    height = img.shape[0]
    img_left = img.copy()
    img_right = img.copy()
    
    img_left[:,:int(height/2)] = 0
    img_right[:,int(height/2):] = 0
    
    #find maxima
    left_psf_loc = np.unravel_index(np.argmax(img_left),img.shape)
    right_psf_loc = np.unravel_index(np.argmax(img_right),img.shape)
    
    #DEBUG show location of psf's
    #img[left_psf_loc] = 100
    #img[right_psf_loc] = 100
    #plotfast.image(img)
    shape = img.shape
    A = np.zeros(shape,dtype=float)
    B = A.copy()
    
    return (left_psf_loc, right_psf_loc)

#if error radius might be to large
def extract_psfs(img, left_loc, right_loc, init_radius=0.20):
    x_start = int(left_loc[0] - init_radius*img.shape[0])
    x_stop = int(left_loc[0] + init_radius*img.shape[0])
    
    y_start = int(left_loc[1] - init_radius*img.shape[1])
    y_stop = int(left_loc[1] + init_radius*img.shape[1])
    #copy psf's
    left_psf = img[x_start:x_stop, y_start:y_stop]
    
    x_start = int(right_loc[0] - init_radius*img.shape[0])
    x_stop = int(right_loc[0] + init_radius*img.shape[0])
    
    y_start = int(right_loc[1] - init_radius*img.shape[1])
    y_stop = int(right_loc[1] + init_radius*img.shape[1])
    
    right_psf = img[x_start:x_stop, y_start:y_stop]  
    return (left_psf, right_psf)

def gen_adi_dataset(angular_seperation, time_between_exposures, numb):
    
    #set disk properties
    disk_without_star = d.disk(field_size=10, with_star=False, inner_radius=1,
                        outer_radius=8, rotation=0, inclination=80)
    disk_with_star = d.disk(field_size=10, with_star=True, inner_radius=5,
                     outer_radius=8, rotation=0, inclination=80)
    
    #process disk without center star
#    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_without_star, angular_seperation)
    #plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube_without_star, img_params_without_star) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    #process disk with center star
    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_with_star, angular_seperation)
    #plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube, img_params) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    return (img_cube, img_params, img_cube_without_star, img_params_without_star)
    
def adi(img_cube, img_params):
    #select single psf from img
#    #do adi
    median = np.median(img_cube, axis=0)
    I_adi = []
    a = 0.8; b=2; c=2
    for i in range(b,len(img_cube)-c):    
        I_d = img_cube[i] - median
        #store I_d -median 1.5 FHWM and the rotation of I_d which is the 
        #second param of img_params in the I_adi list
        I_adi.append( (I_d - a*np.median(img_cube[i-b:i+c], axis=0), img_params[i][0]) )
    
    I_f = []
    for i,(I,rotation) in enumerate(I_adi):
        rotated = ndimage.rotate(I, -rotation, reshape=False)#TODO better params
        I_f.append(rotated[:])
    print(I_f)
    I_f = np.median(np.array(I_f), axis=0)
    print(I_f)
    
    plotfast.image(np.abs(I_f))
    
    
if __name__ == "__main__":
    (img_cube, img_params, img_cube_without_star, img_params_without_star) = gen_adi_dataset(3, 0.01, 100)
    img_cube = img_cube_without_star
    img_params = img_params_without_star
    
    left_psfs = []
    for img in img_cube:
        (left, right) = find_sub_psf_location(img)
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
    
    adi(left_psfs, img_params)
    #adi(right_psfs, img_params)
