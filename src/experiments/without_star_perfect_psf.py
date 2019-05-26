from code.adi import *

def gen_disk_dataset_without_star_perfect_psf(field_size: float, 
    inner_radius: float, outer_radius: float, rotation: float, inclination: float, 
    set_rotation: float, numb: int, rings=None
    ):
    # set disk properties
    disk_without_star = disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
                               outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = disk(field_size=field_size, with_star=True, inner_radius=inner_radius,
                            outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        numb, disk_without_star, set_rotation)

    (ref_cube, ref_params) = d.gen_cube(
        numb, disk_with_star, set_rotation)

    # lazily create psf cube
    clean_psf = psf.get_clean().flatten()
    psf_cube = [clean_psf for i in range(0, numb)]
    psf_params = [0 for i in range(0, numb)]

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

    field_size: float = 10 
    inner_radius: float = 2
    outer_radius: float = 3
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    numb: int = 20
    
    output_path = get_output_path("without_star_perfect_psf")

    (ref_cube, img_cube, img_params) = gen_disk_dataset_without_star_perfect_psf(field_size, inner_radius, outer_radius, 
        rotation, inclination, set_rotation, numb)
    write_metadata(output_path+"meta",
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