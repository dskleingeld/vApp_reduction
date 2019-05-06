from code.adi import *

def gen_disk_dataset_without_star(time_between_exposures: float, fried_parameter: float, field_size: float, 
    inner_radius: float, outer_radius: float, rotation: float, inclination: float, 
    set_rotation: float, numb: int
    ):
    # set disk properties
    disk_without_star = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
                               outer_radius=outer_radius, rotation=rotation, inclination=inclination)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=field_size, with_star=True, inner_radius=inner_radius,
                            outer_radius=outer_radius, rotation=rotation, inclination=inclination)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_without_star, set_rotation)

    (ref_cube, ref_params) = d.gen_cube(
        numb, disk_with_star, set_rotation)

    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=fried_parameter, time_between=time_between_exposures)

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

    time_between_exposures: float = 0.7
    fried_parameter: float = 4
    field_size: float = 10 
    inner_radius: float = 2
    outer_radius: float = 3
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    numb: int = 20

    output_path = get_output_path("without_star")

    (ref_cube, img_cube, img_params) = gen_disk_dataset_without_star(time_between_exposures, fried_parameter, field_size, inner_radius, outer_radius, 
        rotation, inclination, set_rotation, numb)
    write_metadata(output_path+"meta", time_between_exposures=time_between_exposures, fried_parameter=fried_parameter, 
        field_size=field_size, inner_radius=inner_radius, outer_radius=outer_radius, rotation=rotation, inclination=inclination, 
        set_rotation=set_rotation, numb=numb)

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

    save_to_fits(output_path+"right_psfs",right_psfs)
    save_to_fits(output_path+"left_psfs",left_psfs) 

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    save_to_fits(output_path+"right_final",right_final)
    save_to_fits(output_path+"left_final",left_final)