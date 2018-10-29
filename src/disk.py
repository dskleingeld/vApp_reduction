import numpy as np

class properties:
    def __init__(self, field_size, luminosity_star=1.0,inclination=30, 
    rotation=30, inner_radius=None,outer_radius=None, with_star=True):
        
        self.luminosity_star = luminosity_star
        self.L = field_size
        self.inclination = inclination *np.pi/180
        if inner_radius is None: self.inner_radius = 1/field_size
        else : self.inner_radius = inner_radius
        if outer_radius is None: self.outer_radius = field_size
        else : self.outer_radius = outer_radius
        self.rotation = rotation *np.pi/180
        self.with_star= with_star
        print(with_star)
        
def from_properties(dp: properties, resolution: int = 400) -> np.array:

    AU = 1
    L = dp.L * AU 
    inner_radius = dp.inner_radius * AU
    outer_radius = dp.outer_radius * AU
        
    Star = np.full([resolution,resolution], dp.luminosity_star)
    X = np.linspace(-L, L, resolution)
    Y = np.linspace(-L, L, resolution)
    
    XX, YY = np.meshgrid(X, Y)  # Observed xy frame
    ang = np.arctan2(YY, XX) - dp.rotation# (YY*AU, XX*AU) - rot
    R0 = np.hypot(XX, YY)# np.hypot(YY*AU, XX*AU) # Observed radius
    Xt = R0*np.cos(ang)
    Yt = R0*np.sin(ang)/np.cos(dp.inclination)
    Rr = np.hypot(Xt, Yt)  # Real radius
    D = 4*np.pi*(Rr)**2

	#TODO MAJOR MISTAKE IN THIS MODDEL. 
	#model is comparing 0 radius star with a disk with a real radius
	#giving an infinitely smaller disk, due to floating point rounded to
	#e-27 or some other rediculouse thing

    field = np.zeros([resolution,resolution])
    field[(Rr>inner_radius) & (Rr<outer_radius)] = np.divide(Star[(Rr>inner_radius) & (Rr<outer_radius)], 
                 D[(Rr>inner_radius) & (Rr<outer_radius)],
                 out = Star[(Rr>inner_radius) & (Rr<outer_radius)],
                #Intensity of 1/R**2, with inner_radius and outer_radius
                 where = Rr[(Rr>inner_radius) & (Rr<outer_radius)] != 0)  
    
    if dp.with_star == True:
        print("placing star")
        field[int(field.shape[0]/2),int(field.shape[1]/2)] = dp.luminosity_star
    
    if inner_radius == 0:
        print("inner_rad is nul")
        field[(XX == 0) & (YY == 0)] = field.max()
    
    if True: #debugplot
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
