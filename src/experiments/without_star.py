from code.adi import *

def gen_disk_dataset_without_star(angular_seperation, time_between_exposures, numb):
    # set disk properties
    disk_without_star = d.disk(field_size=10, with_star=False, inner_radius=2,
                               outer_radius=3, rotation=0, inclination=80)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=10, with_star=True, inner_radius=2,
                            outer_radius=3, rotation=0, inclination=80)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_without_star, angular_seperation)

    (ref_cube, ref_params) = d.gen_cube(
        numb, disk_with_star, angular_seperation)

    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=4, time_between=0.7)

    # lazily convolve signals
    (img_cube, img_params) = psf.convolve_cube(
        psf_cube, disk_cube, psf_params, disk_params)
    (ref_cube, _) = psf.convolve_cube(
        psf_cube, ref_cube, psf_params, ref_params)
    return (
        ref_cube,
        img_cube,
        img_params)

def run():
    (ref_cube, img_cube, img_params) = gen_disk_dataset_without_star(60, 0.1, 100)

    clean_psf = psf.get_clean()
    (_, shift_cube) = center_cube(ref_cube, ref_img=clean_psf)#TODO doesnt work for no star psf (use star image)
    img_cube = center_cube(img_cube, shifts=shift_cube)

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

    #plotfast.image(np.asarray(right_psfs))
    save_to_fits("without_star/right_psfs",right_psfs)

    right_final = simple_adi(right_psfs, img_params)
    #print(right_final)
    plotfast.image(np.asarray(right_final))

    save_to_fits("without_star/right_final",right_final)