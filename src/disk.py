import numpy as np

class properties:
    def __init__(self, field_size=8, steller_surface_flux=1.0, steller_radius=0.00465, inclination=30, 
    rotation=30, inner_radius=None,outer_radius=None, with_star=True):
        
        self.F_star = steller_surface_flux
        self.R_star = steller_radius
        
        self.L = field_size
        self.inclination = inclination *np.pi/180
        if inner_radius is None: self.inner_radius = 1
        else : self.inner_radius = inner_radius
        if outer_radius is None: self.outer_radius = 5
        else : self.outer_radius = outer_radius
        self.rotation = rotation *np.pi/180
        self.with_star= with_star
        print(with_star)
        
def from_properties(dp: properties, resolution: int = 400) -> np.array:

    L = dp.L
    R_inner = dp.inner_radius
    R_outer = dp.outer_radius
        
    Star = np.full([resolution,resolution], dp.F_star)
    X = np.linspace(-L, L, resolution)
    Y = np.linspace(-L, L, resolution)
    
    XX, YY = np.meshgrid(X, Y)  # Observed xy frame
    ang = np.arctan2(YY, XX) - dp.rotation# (YY*AU, XX*AU) - rot
    R0 = np.hypot(XX, YY)# np.hypot(YY*AU, XX*AU) # Observed radius
    Xt = R0*np.cos(ang)
    Yt = R0*np.sin(ang)/np.cos(dp.inclination)
    Rr = np.hypot(Xt, Yt)  # Real radius
    inverse_square_law = (Rr/dp.R_star)**2

    field = np.zeros([resolution,resolution])
    field[(Rr>R_inner) & (Rr<R_outer)] = np.divide(Star[(Rr>R_inner) & (Rr<R_outer)], 
                 inverse_square_law[(Rr>R_inner) & (Rr<R_outer)],
                 out = Star[(Rr>R_inner) & (Rr<R_outer)],
                #Intensity of 1/R**2, with inner_radius and outer_radius
                 where = Rr[(Rr>R_inner) & (Rr<R_outer)] != 0)  
    
    if dp.with_star == True:
        print("placing star")
        field[int(field.shape[0]/2),int(field.shape[1]/2)] = dp.luminosity_star
    
    if R_inner == 0:
        print("inner_rad is nul")
        field[(XX == 0) & (YY == 0)] = field.max()
    
    if False: #debugplot
        from matplotlib import pyplot as plt
        plt.clf()
        plt.imshow(field, interpolation='none', origin = 'lower',
                   cmap = plt.get_cmap('afmhot'))
        plt.colorbar(label = 'Relative luminosity')
        plt.title('Intensity profile')
        plt.show()
    
    return field
    
if __name__ == "__main__":
    test = properties(10, inner_radius=4, outer_radius=9, with_star=False)
    from_properties(test)
