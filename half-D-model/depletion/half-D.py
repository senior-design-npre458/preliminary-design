import openmc
import openmc.mgxs
import openmc.deplete
model = openmc.Model()
materials = openmc.Materials.from_xml('../msbr/msbr-materials.xml')

homogenous = openmc.Material(name = 'homogenous')
dens = 0.0
for mat in materials:
    if mat.name == 'graphite':
        pass
    else:
        for nuc, ao in mat.get_nuclide_atom_densities().items():
            homogenous.add_nuclide(nuc, ao)
        dens += mat.density
        dens_units = mat.density_units
homogenous.set_density(dens_units, dens/2)
homogenous.add_s_alpha_beta('c_Graphite',.5)
homogenous.volume = 3.14*9**2*20
model.materials = openmc.Materials([homogenous])

bottom, top = [openmc.ZPlane(z0 = v, boundary_type = 'vacuum') for v in [-10,10]] 
cyl = openmc.ZCylinder(r=9,boundary_type = 'reflective')
cell = openmc.Cell(name = 'core', fill = homogenous, region= -cyl & +bottom & -top)
uni = openmc.Universe(cells = [cell])
model.geometry.root_universe = uni

model.settings.particles = 1000
model.settings.batches = 100
model.settings.inactive = 50
model.settings.source = openmc.IndependentSource(space=openmc.stats.Box([-9, -9, -10], 
                                                                        [9, 9, 10]), constraints = {'fissionable':True})

operator = openmc.deplete.CoupledOperator(model, 'chain_endfb71_pwr.xml')
integrator = openmc.deplete.CECMIntegrator(operator=operator, timesteps=[10*n for n in range(1,37)], power=1e9)

integrator.integrate(output=False)
