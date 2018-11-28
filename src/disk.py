import numpy as np
from multiprocessing import Pool
from functools import partial
from copy import deepcopy

def to_radians(deg):
    return deg *np.pi/180

class disk:
    def __init__(self, field_size=8, steller_surface_flux=1.0, steller_radius=0.00465, inclination=30, 
    rotation=30, inner_radius=None, outer_radius=None, with_star=True):
        
        self.F_star = steller_surface_flux
        self.R_star = steller_radius
        
        self.L = field_size
        self.inclination = inclination *np.pi/180
        if inner_radius is None: self.inner_radius = 1
        else : self.inner_radius = inner_radius
        if outer_radius is None: self.outer_radius = 5
        else : self.outer_radius = outer_radius
        self.rotation = to_radians(rotation)
        self.with_star= with_star
        self.resolution = 200
        self.field = None 
    
    def render(self):
        L = self.L
        R_inner = self.inner_radius
        R_outer = self.outer_radius
            
        Star = np.full([self.resolution,self.resolution], self.F_star)
        X = np.linspace(-L, L, self.resolution)
        Y = np.linspace(-L, L, self.resolution)
        
        XX, YY = np.meshgrid(X, Y)  # Observed xy frame
        ang = np.arctan2(YY, XX) - self.rotation# (YY*AU, XX*AU) - rot
        R0 = np.hypot(XX, YY)# np.hypot(YY*AU, XX*AU) # Observed radius
        Xt = R0*np.cos(ang)
        Yt = R0*np.sin(ang)/np.cos(self.inclination)
        Rr = np.hypot(Xt, Yt)  # Real radius
        inverse_square_law = (Rr/self.R_star)**2

        field = np.zeros([self.resolution,self.resolution])
        field[(Rr>R_inner) & (Rr<R_outer)] = np.divide(Star[(Rr>R_inner) & (Rr<R_outer)], 
                     inverse_square_law[(Rr>R_inner) & (Rr<R_outer)],
                     out = Star[(Rr>R_inner) & (Rr<R_outer)],
                    #Intensity of 1/R**2, with inner_radius and outer_radius
                     where = Rr[(Rr>R_inner) & (Rr<R_outer)] != 0)  
        
        if R_inner == 0:
            print("inner_rad is nul")
            field[(XX == 0) & (YY == 0)] = field.max()
        
        if self.with_star:
            field[int(field.shape[0]/2), int(field.shape[1]/2)] = self.F_star
        
        if False: #debugplot
            from matplotlib import pyplot as plt
            plt.clf()
            plt.imshow(field, interpolation='none', origin = 'lower',
                       cmap = plt.get_cmap('afmhot'))
            plt.colorbar(label = 'Relative luminosity')
            plt.title('Intensity profile')
            plt.show()
        
        self.field = field        
    
    def to_list(self):
        return [self.rotation, self.field]
        
    def paramslist(self):
        return [self.F_star, self.R_star, self.L, self.inclination, self.inner_radius, 
                self.outer_radius, self.with_star, self.resolution]

def rotate(clean_disk, theta):
    rotated_disk = deepcopy(clean_disk)
    rotated_disk.rotation += to_radians(theta)
    rotated_disk.render()
    return rotated_disk.to_list()

def gen_cube(num, clean_disk, angular_sep):
    print("generating disk cube")
    params = clean_disk.paramslist()
    angles = np.linspace(0,angular_sep, num)
    func = partial(rotate, clean_disk)
    with Pool(processes=16) as pool:
        cube_list = pool.map(func, angles)
        
    def add_disk_params(c_list):
        rotation = c_list[0]
        diskp = deepcopy(params)
        diskp[-1] = rotation
        return diskp
        
    cube_params = list(map(add_disk_params, cube_list))
    disk_cube = list(map(lambda x: x[1], cube_list))
    return disk_cube, cube_params

if __name__ == "__main__":
    test = properties(10, inner_radius=4, outer_radius=9, with_star=False)
    from_properties(test)
