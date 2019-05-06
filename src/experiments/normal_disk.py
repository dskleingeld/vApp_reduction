from code.adi import *

def run():
    
    time_between_exposures: float = 0.7
    fried_parameter: float = 4
    field_size: float = 10 
    inner_radius: float = 2
    outer_radius: float = 5
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    numb: int = 20
    
    output_path = get_output_path("normal_disk")

    (img_cube, img_params) = gen_disk_dataset(time_between_exposures, fried_parameter, field_size, inner_radius, outer_radius, 
        rotation, inclination, set_rotation, numb)
    write_metadata(output_path+"meta", time_between_exposures=time_between_exposures, fried_parameter=fried_parameter, 
        field_size=field_size, inner_radius=inner_radius, outer_radius=outer_radius, rotation=rotation, inclination=inclination, 
        set_rotation=set_rotation, numb=numb)

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

    #plotfast.image(np.asarray(right_psfs))
    save_to_fits(output_path+"right_psfs",right_psfs)
    save_to_fits(output_path+"left_psfs",left_psfs) 

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    save_to_fits(output_path+"right_final",right_final)
    save_to_fits(output_path+"left_final",left_final)
    plotfast.image(np.asarray(right_final))
