from code.adi import *

def run():
    (img_cube, img_params) = gen_disk_dataset(60, 0.1, 100)

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
    right_final = simple_adi(right_psfs, img_params)
    plotfast.image(right_final)

    save_to_fits("normal_disk_final",right_final)