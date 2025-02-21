import openmc
import openmc.mgxs as mgxs
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

groups = mgxs.EnergyGroups(group_edges=np.array([0., 20.0e6]))
fission = mgxs.FissionXS(domain=cell, energy_groups=groups, nu = True)
absorption = mgxs.AbsorptionXS(domain=cell, energy_groups=groups)

tallies = openmc.Tallies()
tallies += fission.tallies.values()
tallies += absorption.tallies.values()

model.tallies = tallies

model.run(output=True)

sp = openmc.StatePoint('statepoint.100.h5')

fission.load_from_statepoint(sp)
absorption.load_from_statepoint(sp)

sp.close()

fisxs = fission.get_pandas_dataframe()['mean'].values[0]
absxs = absorption.get_pandas_dataframe()['mean'].values[0]

P = 1e9 / 48710000.0
flux = P / 1.60218e-13 * 200 * fisxs

with open('output.txt','w') as file:
    file.write('fisxs, absxs, flux\n')
    file.write(f'{fisxs},{absxs},{flux}')
    file.close()

uni.plot(pixels=400000)
plt.savefig('geom.png',dpi=600)
plt.close()