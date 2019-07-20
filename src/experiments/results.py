from code.adi import *
import code.plot.slow as plotslow
import code.plot.fast as plotfast
import code.disk as d

from copy import deepcopy

class Params:
    time_between_exposures: float = 20
    numb: int = 20
    fried_parameter: float = 18
    field_size: float = 10 
    rotation: float = 120
    inclination: float = 60 
    set_rotation: float = 60
    rings = [(0.3,0.5)] #percent of radius of rings and gaps, start stop tuples
    amplification=50

#######################################################################################

def gen_disk_dataset_without_star(params):
    # set disk properties
    disk_without_star = d.disk(field_size=params.field_size, with_star=False,
                               rotation=params.rotation, inclination=params.inclination, rings=params.rings)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=params.field_size, with_star=True, rotation=params.rotation, 
                            inclination=params.inclination, rings=params.rings)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        params.numb, disk_without_star, params.set_rotation)

    (ref_cube, ref_params) = d.gen_cube(
        params.numb, disk_with_star, params.set_rotation)

    # lazily create psf cube
    (psf_cube, psf_params) = psf.calc_cube(
        params.numb, fried_parameter=params.fried_parameter, time_between=params.time_between_exposures)

    # lazily convolve signals
    (img_cube, img_params) = psf.convolve_cube(
        psf_cube, disk_cube, psf_params, disk_params)
    (ref_cube, _) = psf.convolve_cube(
        psf_cube, ref_cube, psf_params, ref_params)
    return (
        ref_cube,
        img_cube,
        img_params)

def gen_disk_dataset_without_star_perfect_psf(params):
    # set disk properties
    disk_without_star = d.disk(field_size=params.field_size, with_star=False, rotation=params.rotation, 
                               inclination=params.inclination, rings=params.rings)
    # set disk properties //also need disk with star convolved with same psf for
    # alignment
    disk_with_star = d.disk(field_size=params.field_size, with_star=True, rotation=params.rotation, 
                            inclination=params.inclination, rings=params.rings)

    # create disk cube
    (disk_cube, disk_params) = d.gen_cube(
        params.numb, disk_without_star, params.set_rotation)

    (ref_cube, ref_params) = d.gen_cube(
        params.numb, disk_with_star, params.set_rotation)

    # lazily create psf cube
    clean_psf = psf.get_clean().flatten()
    psf_cube = [clean_psf for i in range(0, params.numb)]
    psf_params = [0 for i in range(0, params.numb)]

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



def noReduction(params, output_path):

    numb = 1
    (img_cube, _img_params) = gen_disk_dataset(params.time_between_exposures, params.fried_parameter, params.field_size,0,0, 
        params.rotation, params.inclination, params.set_rotation, numb, rings=params.rings, amplification=params.amplification)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    #plotfast.image(np.array(left_psfs[0]))

    plotslow.saveImage_withCb(left_psfs[0],output_path+"right_noReductin", log=True, vmin=1e-9, vmax=1e-2)
    plotslow.saveImage_withCb(right_psfs[0],output_path+"left_noReduction", log=True, vmin=1e-9, vmax=1e-2)

def withADI(params, output_path):

    (img_cube, img_params) = gen_disk_dataset(params.time_between_exposures, params.fried_parameter, params.field_size, 0,0, 
        params.rotation, params.inclination, params.set_rotation, params.numb, rings=params.rings, amplification=params.amplification)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(img_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    #plotfast.image(np.array(right_psfs))

    right_final = simple_adi(right_psfs, img_params)
    left_final = simple_adi(left_psfs, img_params)

    plotslow.saveImage_withCb(right_final,output_path+"right_ADI", log=False, vmax=.004*params.amplification)
    plotslow.saveImage_withCb(left_final,output_path+"left_ADI", log=False, vmax=.004*params.amplification) #vmin=.005 at ampl = 10

def coro_psf(params, output_path):

    numb = 1
    (psf_cube, psf_params) = psf.calc_cube(
        numb, fried_parameter=params.fried_parameter, time_between=params.time_between_exposures)
    
    for idx, psf_slicle in enumerate(psf_cube):
        psf_cube[idx] = psf_slicle.reshape(200,200)

    clean_psf = psf.get_clean()
    (img_cube, _) = center_cube(psf_cube, ref_img=clean_psf)

    (left, right) = find_sub_psf_location(clean_psf)

    right_psfs = []
    left_psfs = []
    for img in img_cube:
        (left_psf, right_psf) = extract_psfs(img, left, right)
        left_psfs.append(left_psf)
        right_psfs.append(right_psf)

    #plotfast.image(np.array(left_psfs[0]))
    #data = np.abs(left_psfs[0])
    #clipped = (data/data.max()).clip(min=1e-60)
    #plotfast.image(np.array([np.log10(clipped)]))
    plotslow.saveImage_withCb(left_psfs[0],output_path+"right_coro_psf", log=True)
    plotslow.saveImage_withCb(right_psfs[0],output_path+"left_coro_psf", log=True)

def noStar_noReduction(params, output_path):

    numb=1
    (ref_cube, img_cube, _img_params) = gen_disk_dataset_without_star_perfect_psf(params)

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

    plotslow.saveImage_withCb(left_psfs[0],output_path+"right_no_star_noReductin", log=True)
    plotslow.saveImage_withCb(right_psfs[0],output_path+"left_no_star_noReduction", log=True)

def noStar_ADI(params, output_path):
   
    (ref_cube, img_cube, img_params) = gen_disk_dataset_without_star_perfect_psf(params)

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

    plotslow.saveImage_withCb(right_final,output_path+"right_no_star_ADI", log=False)
    plotslow.saveImage_withCb(left_final,output_path+"left_no_star_ADI", log=False)

def plot_model(params, output_path):
    numb = 1
    model = d.disk(field_size=params.field_size, with_star=True, rotation=params.rotation, 
                   inclination=params.inclination, rings=params.rings, amplification=params.amplification)
    (disk_cube, _disk_params) = d.gen_cube(numb, model, params.set_rotation)

    plotslow.saveImage_withCb(disk_cube[0],output_path+"model", log=True, lim=[[50,150],[50,150]])

def run():
    

    default_params = Params()
    disks = []

    # disks.append(("A", default_params))
    # disks.append(("B", deepcopy(default_params)))
    # disks[-1][1].rings = [(0.1,0.2),(0.3,0.4)]
    # disks.append(("C", deepcopy(default_params)))
    # disks[-1][1].amplification /= 50
    # disks.append(("D", deepcopy(default_params)))
    # disks[-1][1].rings = [(0.3,0.4)]   
    # disks.append(("E", deepcopy(default_params)))
    # disks[-1][1].rings = [(0.1,0.8)]   
    # disks.append(("F", deepcopy(default_params)))
    # disks[-1][1].rings = [(0.1,0.2)]   
    # disks.append(("G", deepcopy(default_params)))
    # disks[-1][1].rotation = 0
    # disks.append(("H", deepcopy(default_params)))
    # disks[-1][1].inclination = 40
    
    params = deepcopy(default_params)
    params.set_rotation = 360
    params.numb = 80
    disks.append(("ADI360", params))

    params = deepcopy(default_params)
    params.set_rotation = 10
    params.numb = 1
    disks.append(("ADI360", params))

    for img_name, params in disks:
        script_path = os.path.realpath(__file__).split("vApp_reduction",1)[0]
        output_path = script_path+"vApp_reduction/plots/results/"+img_name
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_path+= "/"

        write_metadata(output_path+"meta", 
            time_between_exposures=params.time_between_exposures, 
            numb=params.numb,
            fried_parameter=params.fried_parameter, 
            
            field_size=params.field_size, 
            rotation=params.rotation, 
            inclination=params.inclination, 
            set_rotation=params.set_rotation,
            
            rings=params.rings,
            amplification=params.amplification)

        #plot_model(params, output_path)
        #noReduction(params, output_path)
        #withADI(params, output_path)
        #noStar_noReduction(params, output_path)
        #noStar_ADI(params, output_path)
        #coro_psf(params, output_path)