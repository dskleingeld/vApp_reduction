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
def find_sub_psf_location(img, init_radius=0.3, init_rotation=45):
    #gauss_2d(1,4)
    
    shape = img.shape
    A = np.zeros(shape,dtype=float)
    B = A.copy()
    
    rr, cc = sk.circle(shape[0]/2, shape[1]/2, init_radius*min(shape[0]/2, shape[1]/2) )
    A[rr,cc] = 1
    [A_left,A_right] = np.split(A,2)
    [B_left,B_right] = np.split(B,2)
    
    left = np.vstack((A_left, B_right))
    right = np.vstack((B_left, A_right))
    left = ndimage.rotate(left, init_rotation)
    right = ndimage.rotate(right, init_rotation)
    
    
    #todo prepare image by cutting off one of the psf's
    height = img.shape[0]
    img_left = img.copy()
    img_right = img.copy()
    
    img_left[:,:int(height/2)] = 0
    img_right[:,int(height/2):] = 0
    
    left_psf_loc = np.unravel_index(np.argmax(img_left),shape)
    right_psf_loc = np.unravel_index(np.argmax(img_right),shape)
    
    #show location of psf's
    #img[left_psf_loc] = 100
    #img[right_psf_loc] = 100
    #plotfast.image(img)
    return (left_psf_loc, right_psf_loc)

def extract_psfs(img, left_loc, right_loc):

    return (left_psf, right_psf)

def adi(angular_seperation, time_between_exposures, numb):
    
    #set disk properties
    disk_without_star = d.disk(10, with_star=False, inner_radius=1,
                        outer_radius=3, rotation=135, inclination=70)
    disk_with_star = d.disk(10, with_star=True, inner_radius=1,
                     outer_radius=3, rotation=135, inclination=70)
    
    #process disk without center star
#    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_without_star, angular_seperation)
    #plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube_without_star, img_params) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    #process disk with center star
    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(numb, disk_with_star, angular_seperation)
    #plotfast.image(disk_cube[0])
    #lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    #lazily convolve signals
    (img_cube_with_star, img_params) = psf.convolve(psf_cube, disk_cube, psf_params, disk_params)
    
    #select interesting region
    test_img = img_cube_with_star[0]
    
    (left, right) = find_sub_psf_location(test_img)
    
    
#    #do adi
#    median = np.median(img_cube_with_star, axis=0)
#    I_adi = []
#    a = 0.1; b=2; c=2
#    for i in range(b,len(img_cube_with_star)-c):    
#        I_d = img_cube_with_star[i] - median
#        I_adi.append( I_d - a*np.median(img_cube_with_star[i-b..i+c])
#    
#    I_f = 0
#    for i,I in enumerate(I_adi):
#        I(i)
        
    #plotfast.image(img_cube_with_star-mean)
    
    
if __name__ == "__main__":
    adi(10, 0.7, 10)
