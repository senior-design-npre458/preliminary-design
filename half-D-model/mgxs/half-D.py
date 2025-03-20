import openmc
import openmc.mgxs as mgxs
import openmc.deplete
import numpy as np
import matplotlib.pyplot as plt

model = openmc.Model()
materials = openmc.Materials.from_xml('../msbr/msbr-materials.xml')

'''homogenous = openmc.Material(name = 'homogenous')
dens = 0.0
for mat in materials:
    if mat.name == 'fuel':
        for nuc, ao in mat.get_nuclide_atom_densities().items():
            homogenous.add_nuclide(nuc, ao)
        dens += mat.density
        dens_units = mat.density_units
homogenous.set_density(dens_units, dens)
homogenous.volume = 48710000.0
'''
fuel = materials[0]
fuel.add_nuclide('U233',0.025,'wo')
model.materials = openmc.Materials([fuel])

bottom, top = [openmc.ZPlane(z0 = v, boundary_type = 'reflective') for v in [-1000,1000]] 
cyl = openmc.ZCylinder(r=900,boundary_type = 'reflective')
cell = openmc.Cell(name = 'core', fill = fuel, region= -cyl & +bottom & -top)
uni = openmc.Universe(cells = [cell])
model.geometry.root_universe = uni

model.settings.particles = 10000
model.settings.batches = 100
model.settings.inactive = 50
model.settings.source = openmc.IndependentSource(space=openmc.stats.Box([-900, -900, -1000], 
                                                                        [900, 900, 1000]), constraints = {'fissionable':True})

filename = '../depletion/chain_endfb71_pwr.xml'
operator = openmc.deplete.CoupledOperator(model,filename)
micro_xs = openmc.deplete.get_microxs_and_flux(model=model,domains=[uni],
                nuclides = ['Xe135','Th232','Pa233'],energies=[0., 20.0e6],chain_file=filename, run_kwargs={'output': False})

xs = micro_xs[1][0]
total_abs = []
transmute = []
'''
reactions : ['(n,gamma)', '(n,2n)', '(n,p)', '(n,a)', '(n,3n)', '(n,4n)', 'fission']
'''
for nuc, data in zip(xs.nuclides, xs.data):
    total_abs.append(np.str_(np.sum(data)))
    transmute.append(np.str_(data[0][0]))

with open('output.txt','w') as file:
    file.write(', '.join(xs.nuclides))
    file.write('\n')
    file.write(', '.join(total_abs))
    file.write('\n')
    file.write(', '.join(transmute))
    file.close()