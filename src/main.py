import psf.from_simulated_psf as psf
import disk as d
import plot.fast as plotfast
import numpy as np
from scipy import signal, ndimage


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
    x_start = int(left_loc[0] - init_radius * img.shape[0])
    x_stop = int(left_loc[0] + init_radius * img.shape[0])

    y_start = int(left_loc[1] - init_radius * img.shape[1])
    y_stop = int(left_loc[1] + init_radius * img.shape[1])
    # copy psf's
    left_psf = img[x_start:x_stop, y_start:y_stop]

    x_start = int(right_loc[0] - init_radius * img.shape[0])
    x_stop = int(right_loc[0] + init_radius * img.shape[0])

    y_start = int(right_loc[1] - init_radius * img.shape[1])
    y_stop = int(right_loc[1] + init_radius * img.shape[1])

    right_psf = img[x_start:x_stop, y_start:y_stop]
    return (left_psf, right_psf)


def gen_adi_dataset(angular_seperation, time_between_exposures, numb):

    # set disk properties
    disk_without_star = d.disk(field_size=10, with_star=False, inner_radius=2,
                               outer_radius=3, rotation=0, inclination=60)
    disk_with_star = d.disk(field_size=10, with_star=True, inner_radius=2,
                            outer_radius=3, rotation=0, inclination=60)

    # process disk without center star
#    #create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_without_star, angular_seperation)
    # plotfast.image(disk_cube[0])
    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=4, time_between=0.7)
    # plotfast.image(psf_cube[0].reshape(200,200))
    # lazily convolve signals
    (img_cube_without_star, img_params_without_star) = psf.convolve(
        psf_cube, disk_cube, psf_params, disk_params)

    # process disk with center star
    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_with_star, angular_seperation)
    # plotfast.image(disk_cube[0])
    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=4, time_between=0.7)
    # lazily convolve signals
    (img_cube, img_params) = psf.convolve(
        psf_cube, disk_cube, psf_params, disk_params)

    return (
        img_cube,
        img_params,
        img_cube_without_star,
        img_params_without_star)


def gen_adi_star_controlset(total_angle, numb):
    angular_seperation = total_angle / numb

    star = np.zeros((200, 200))
    star[int(star.shape[0] / 2), int(star.shape[1] / 2)] = 1

    (psf_cube, psf_params) = psf.calc_cube(
        1, fried_parameter=4, time_between=0.7)
    img = signal.convolve2d(
        psf_cube[0].reshape(
            200,
            200),
        star,
        boundary='symm',
        mode='same')
    # plotfast.image(img)

    img_cube = [img.copy() for i in range(0, numb)]
    img_params = [[angular_seperation * i] for i in range(0, numb)]

    return (img_cube, img_params)


def gen_adi_binary_controlset(total_angle, numb):

    field = np.zeros((200, 200))
    field[int(field.shape[0] / 2), int(field.shape[1] / 2)] = 1
    field[int(field.shape[0] / 3), int(field.shape[1] / 3)] = 0.01  # companion

    field_cube = [ndimage.rotate(field.copy(), angle, reshape=False)
                  for angle in np.linspace(0, total_angle, num=numb)]
    field_params = [[angle] for angle in np.linspace(0, total_angle, num=numb)]

    (single_psf, psf_param) = psf.calc_cube(
        1, fried_parameter=4, time_between=0.7)
    psf_cube = [single_psf.copy() for i in range(0, numb)]
    psf_params = [psf_param.copy() for i in range(0, numb)]
    
    print(len(field_cube))
    print(len(field_params))
    print(len(psf_cube))
    print(len(psf_params))
    # (psf_cube, psf_params) = psf.calc_cube(numb, fried_parameter=4, time_between=0.7)
    (img_cube, img_params) = psf.convolve(
        psf_cube, field_cube, psf_params, field_params)
    print(img_cube)
    # plotfast.image(np.asarray(img_cube))

    return (img_cube, img_params)


def adi(img_cube, img_params):
    # select single psf from img
    #    #do adi
    median = np.median(img_cube, axis=0)
    I_adi = []
    a = 0
    b = 4
    c = 4
    for i in range(b, len(img_cube) - c):
        I_d = img_cube[i] - median
        print("lala")
        # store I_d -median 1.5 FHWM and the rotation of I_d which is the
        # second param of img_params in the I_adi list
        I_adi.append(
            (I_d - a * np.median(img_cube[i - b:i + c], axis=0), img_params[i][0]))

    I_f = []
    for (I, rotation) in I_adi:
        rotated = ndimage.rotate(I, -rotation, reshape=False)
        I_f.append(rotated[:])
    I_f = np.median(np.array(I_f), axis=0)
    plotfast.image(I_adi[0][0])
    # plotfast.image(I_f)
    # plotfast.image(np.abs(I_f))


def simple_adi(img_cube, img_params):
    median = np.median(img_cube, axis=0)
    rotation = [param[0] for param in img_params]
    I = []
    for (img, angle) in zip(img_cube, rotation):
        derotated = ndimage.rotate((img - median), -angle, reshape=False)
        I.append(derotated)
    I = np.median(np.array(I), axis=0)
    # plotfast.image(I)


if __name__ == "__main__":
    #    (img_cube, img_params, img_cube_without_star, img_params_without_star) = gen_adi_dataset(0.60, 0.1, 100)
    #    (img_cube, img_params) = gen_adi_star_controlset(60,100)
    (img_cube, img_params) = gen_adi_binary_controlset(60, 70)

    left_psfs = []
    right_psfs = []
    for img in img_cube:
        (left, right) = find_sub_psf_location(img)
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)
    plotfast.image(np.asarray(left_psfs))
    simple_adi(left_psfs, img_params)
    #adi(right_psfs, img_params)

#    img_cube = img_cube_without_star
#    plotfast.image(img_cube)
#    img_params = img_params_without_star
#
#    left_psfs = []
#    right_psfs = []
#    for img in img_cube:
#        (left, right) = find_sub_psf_location(img)
#        (left_psf, right_psf) = extract_psfs(img, left, right)
#        left_psfs.append(left_psf); right_psfs.append(right_psf)
#
#    adi(left_psfs, img_params)
#    #adi(right_psfs, img_params)
