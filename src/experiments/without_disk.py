from code.adi import *

def gen_adi_star_controlset(total_angle, numb):
    angular_seperation = total_angle / numb

    star = np.zeros((200, 200))
    star[int(star.shape[0] / 2), int(star.shape[1] / 2)] = 1
    field_cube = [star.copy() for i in range(0,numb)]
    field_params = [[angular_seperation * i] for i in range(0, numb)]

    print(field_cube)

    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=4, time_between=0.7)
    (img_cube, img_params) = psf.convolve_cube(psf_cube, field_cube, psf_params, field_params)

    return (img_cube, img_params)

def run():
    (img_cube, img_params) = gen_adi_star_controlset(60,100)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    #(left, right) = find_sub_psf_location_from_cube(img_cube)
    ##alternatively use coords from perfect psf
    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    #combine left and right psfs into one
    # for (left_psf, right_psf) in zip(left_psfs, right_psfs):
    #     psf_combined = left_psf.copy()
    #     psf_combined = right_psf
        #TODO array with indexes + something with np where to split that into left
        #and right indexes


    save_to_fits("without_disk/right_psfs",right_psfs)
    #plotfast.image(np.asarray(right_psfs))
    right_final = simple_adi(right_psfs, img_params)
    plotfast.image(right_final)

    save_to_fits("without_disk/right_final",right_final)
