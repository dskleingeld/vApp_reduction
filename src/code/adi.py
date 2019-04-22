import numpy as np
from scipy import signal, ndimage
from skimage.feature import register_translation
from astropy.io import fits
import copy
import math
import os

from code.psf import from_simulated_psf as psf
import code.disk as d
import code.plot.fast as plotfast

def center(img, ref_img):
    offset_image = img
    shift, error, diffphase = register_translation(ref_img, offset_image, 10)

    img = ndimage.interpolation.shift(img, shift, order=3)
    return (img, shift)

#center with a given shift (gotten from the center funct above)
def center_wshift(img, shift):
    img = ndimage.interpolation.shift(img, shift, order=3)
    return (img)

def center_cube(offset_cube, ref_img=None, shifts=None):
    if shifts == None:
        img_cube = []
        shift_cube = []
        for offset in offset_cube:
            (centerd, shift) = center(offset, ref_img);
            img_cube.append(centerd)
            shift_cube.append(shift)

        return (img_cube, shift_cube)
    else:
        img_cube = []
        for (offset, shift) in zip(offset_cube,shifts):
            centerd = center_wshift(offset, shift);
            img_cube.append(centerd)

        return img_cube


# radius numb between 0 and 1
def find_sub_psf_location(img):
    # prepare image by cutting off one of the psf's
    height = img.shape[0]
    img_left = img.copy()
    img_right = img.copy()

    img_left[:, :int(height / 2)] = 0
    img_right[:, int(height / 2):] = 0

    # find maxima
    left_psf_loc = np.unravel_index(np.argmax(img_left), img.shape)
    right_psf_loc = np.unravel_index(np.argmax(img_right), img.shape)

    return (left_psf_loc, right_psf_loc)


# if error radius might be to large
def extract_psfs(img, left_loc, right_loc, init_radius=0.15):
    #pad image with zero values
    n = 100
    img = np.pad(img,(n,n),"constant")

    x_start = int(left_loc[0]+n - init_radius * img.shape[0])
    x_stop = int(left_loc[0]+n + init_radius * img.shape[0])

    y_start = int(left_loc[1]+n - init_radius * img.shape[1])
    y_stop = int(left_loc[1]+n + init_radius * img.shape[1])
    # copy psf's
    left_psf = img[x_start:x_stop, y_start:y_stop]

    x_start = int(right_loc[0]+n - init_radius * img.shape[0])
    x_stop = int(right_loc[0]+n + init_radius * img.shape[0])

    y_start = int(right_loc[1]+n - init_radius * img.shape[1])
    y_stop = int(right_loc[1]+n + init_radius * img.shape[1])

    right_psf = img[x_start:x_stop, y_start:y_stop]
    return (left_psf, right_psf)


def gen_disk_dataset_without_star(angular_seperation, time_between_exposures, numb):

    # set disk properties
    disk_without_star = d.disk(field_size=10, with_star=False, inner_radius=2,
                               outer_radius=3, rotation=0, inclination=60)

    # process disk with center star
    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_without_star, angular_seperation)
    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=4, time_between=0.7)
    # plotfast.image(psf_cube[0].reshape(200,200))
    # lazily convolve signals
    (img_cube, img_params) = psf.convolve_cube(
        psf_cube, disk_cube, psf_params, disk_params)
    return (
        img_cube,
        img_params)

def write_metadata(path: str, **keywords):
    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    plot_path = script_path+"vApp_reduction/plots/" #TODO rename plot path to "out"?

    with open(plot_path+path+".txt", 'w') as meta:
        for (keyword, value) in keywords.items():
            print(keyword, "=", value, file=meta)

def gen_disk_dataset(time_between_exposures: float, fried_parameter: float, field_size: float, 
    inner_radius: float, outer_radius: float, rotation: float, inclination: float, 
    set_rotation: float, numb: int):

    # set disk properties
    disk_with_star = d.disk(field_size=field_size, with_star=True, inner_radius=inner_radius,
        outer_radius=outer_radius, rotation=rotation, inclination=inclination)

    # process disk with center star
    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_with_star, set_rotation)
    #plotfast.image(disk_cube[0])
    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=fried_parameter, time_between=time_between_exposures)
    # lazily convolve signals
    (img_cube, img_params) = psf.convolve_cube(
        psf_cube, disk_cube, psf_params, disk_params)

    return (
        img_cube,
        img_params)

def gen_adi_binary_controlset(total_angle, numb):

    field = np.zeros((200, 200))
    field[int(field.shape[0] / 2), int(field.shape[1] / 2)] = 1
    field[int(field.shape[0] / 2 - 40), int(field.shape[1] / 2)] = 0.01  # companion

    field_cube = [ndimage.rotate(field.copy(), angle, reshape=False, order=0)
                  for angle in np.linspace(0, total_angle, num=numb)]
    # plotfast.image(np.asarray(field_cube))
    field_params = [[angle] for angle in np.linspace(0, total_angle, num=numb)]

    (psf_cube, psf_params) = psf.calc_cube(
        1, fried_parameter=4, time_between=0.7)

    single_psf = psf_cube[0]; psf_param = psf_params[0]
    psf_cube = [single_psf.copy() for i in range(0, numb)]
    psf_params = [psf_param for i in range(0, numb)]

    # (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)

    (img_cube, img_params) = psf.convolve_cube(
        psf_cube, field_cube, psf_params, field_params)
    # print(img_cube)
    # plotfast.image(np.asarray(img_cube))

    return (img_cube, img_params)


def simple_adi(img_cube, img_params):
    median = np.median(img_cube, axis=0)
    rotation = [param[1][-1] for param in img_params]
    I = []
    I_without_sub = []
    img_cube2 = copy.deepcopy(img_cube)
    for (img, angle) in zip(img_cube, rotation):
        derotated_without_sub = ndimage.rotate(img, math.degrees(angle), reshape=False)
        derotated = ndimage.rotate(img-median, math.degrees(angle), reshape=False)
        I.append(derotated)
        I_without_sub.append(derotated_without_sub)

    #plotfast.image(np.array(img_cube))
    I = np.median(np.array(I), axis=0)
    return I

##use average to determine psf loc
def find_sub_psf_location_from_cube(img_cube):
    left_x=0; left_y=0
    right_x=0; right_y=0
    for img in img_cube:
        (left, right) = find_sub_psf_location(img)
        left_x += left[0]; left_y += left[1]
        right_x += right[0]; right_y += right[1]

    left = (left_x/len(img_cube), left_y/len(img_cube))
    right = (right_x/len(img_cube), right_y/len(img_cube))
    return (left, right)

def save_to_fits(name: str, array):
    #array = 2d_array.flatten()
    script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
    plot_path = script_path+"vApp_reduction/plots/"
    
    folder = name.split("/")[0]
    if not os.path.exists(plot_path+folder):
        os.makedirs(plot_path+folder)

    hdu = fits.PrimaryHDU(array)
    hdu.writeto(plot_path+name+".fits", overwrite=True)