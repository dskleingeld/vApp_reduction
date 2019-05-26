from code.adi import *
import code.plot.slow as plotslow
import code.disk as d

time_between_exposures: float = 0.7
fried_parameter: float = 4
field_size: float = 10 
inner_radius: float = 2
outer_radius: float = 5
rotation: float = 120
inclination: float = 60 
set_rotation: float = 60
numb: int = 20
rings = [(0.1,0.2),(0.3,0.4)] #percent of radius of rings and gaps, start stop tuples

#######################################################################################

def gen_disk_dataset_without_star(time_between_exposures: float, fried_parameter: float, field_size: float, 
    inner_radius: float, outer_radius: float, rotation: float, inclination: float, 
    set_rotation: float, numb: int, rings=None
    ):
    # set disk properties
    disk_without_star = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
                               outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=field_size, with_star=True, inner_radius=inner_radius,
                            outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)

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

def gen_disk_dataset_without_star_perfect_psf(field_size: float, 
    inner_radius: float, outer_radius: float, rotation: float, inclination: float, 
    set_rotation: float, numb: int, rings=None
    ):
    # set disk properties
    disk_without_star = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
                               outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=field_size, with_star=True, inner_radius=inner_radius,
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

#######################################################################################



def noReduction(output_path):

    numb = 1
    (img_cube, _img_params) = gen_disk_dataset(time_between_exposures, fried_parameter, field_size, inner_radius, outer_radius, 
        rotation, inclination, set_rotation, numb, rings=rings)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    plotslow.saveImage_withCb(left_psfs[0],output_path+"right_noReductin")
    plotslow.saveImage_withCb(right_psfs[0],output_path+"left_noReduction")

def withADI(output_path):

    (img_cube, img_params) = gen_disk_dataset(time_between_exposures, fried_parameter, field_size, inner_radius, outer_radius, 
        rotation, inclination, set_rotation, numb, rings=rings)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    plotslow.saveImage_withCb(right_final,output_path+"right_ADI")
    plotslow.saveImage_withCb(left_final,output_path+"left_ADI")

def noStar_noReduction(output_path):

    numb=1
    (ref_cube, img_cube, _img_params) = gen_disk_dataset_without_star_perfect_psf(field_size, inner_radius, outer_radius, 
                                       rotation, inclination, set_rotation, numb, rings=rings)

    clean_psf = psf.get_clean()
    (_, shift_cube) = center_cube(ref_cube, ref_img=clean_psf)
    img_cube = center_cube(img_cube, shifts=shift_cube)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    plotslow.saveImage_withCb(left_psfs[0],output_path+"right_noReductin")
    plotslow.saveImage_withCb( right_psfs[0],output_path+"left_noReduction")

def noStar_ADI(output_path):
   
    (ref_cube, img_cube, img_params) = gen_disk_dataset_without_star_perfect_psf(field_size, inner_radius, outer_radius, 
                                       rotation, inclination, set_rotation, numb, rings=rings)

    clean_psf = psf.get_clean()
    (_, shift_cube) = center_cube(ref_cube, ref_img=clean_psf)
    img_cube = center_cube(img_cube, shifts=shift_cube)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    plotslow.saveImage_withCb(right_final,output_path+"right_final")
    plotslow.saveImage_withCb(left_final,output_path+"left_final")

def plot_model(output_path):
    numb = 1
    model = d.disk(field_size=field_size, with_star=False, inner_radius=inner_radius,
                   outer_radius=outer_radius, rotation=rotation, inclination=inclination, rings=rings)
    (disk_cube, _disk_params) = d.gen_cube(numb, model, set_rotation)

    plotslow.saveImage_withCb(disk_cube[0],output_path+"model")

def run():
    
    output_path = get_output_path("rings")
    write_metadata(output_path+"meta", time_between_exposures=time_between_exposures, fried_parameter=fried_parameter, 
        field_size=field_size, inner_radius=inner_radius, outer_radius=outer_radius, rotation=rotation, inclination=inclination, 
        set_rotation=set_rotation, numb=numb)

    plot_model(output_path)
    noReduction(output_path)
    withADI(output_path)
    noStar_noReduction(output_path)
    noStar_ADI(output_path)