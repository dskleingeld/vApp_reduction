from code.adi import *

#generates using only one psf
def gen_adi_star_controlset(time_between_exposures: float, fried_parameter: float, 
    set_rotation: float, numb: int):
    
    angular_seperation = set_rotation / numb

    star = np.zeros((200, 200))
    star[int(star.shape[0] / 2), int(star.shape[1] / 2)] = 1
    field_cube = [star.copy() for i in range(0,numb)]
    field_params = [[angular_seperation * i] for i in range(0, numb)]

    clean_psf = psf.get_clean().flatten()
    psf_cube = [clean_psf for i in range(0, numb)]
    psf_params = [0 for i in range(0, numb)]

    (img_cube, img_params) = psf.convolve_cube(psf_cube, field_cube, psf_params, field_params)

    return (img_cube, img_params)

def run():
        
    time_between_exposures: float = 0.7
    fried_parameter: float = 4
    set_rotation: float = 60
    numb: int = 20

    output_path = get_output_path("without_disk_perfect_psf")

    (img_cube, img_params) = gen_adi_star_controlset(time_between_exposures,fried_parameter, set_rotation, numb)
    write_metadata(output_path+"meta", time_between_exposures=time_between_exposures, fried_parameter=fried_parameter, 
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

    save_to_fits(output_path+"right_psfs",right_psfs)
    save_to_fits(output_path+"left_psfs",left_psfs) 

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    save_to_fits(output_path+"right_final",right_final)
    save_to_fits(output_path+"left_final",left_final)