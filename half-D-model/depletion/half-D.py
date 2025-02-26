import openmc
import openmc.deplete
import openmc.mgxs as mgxs
import numpy as np
import matplotlib.pyplot as plt

openmc.deplete.pool.NUM_PROCESSES = 1

model = openmc.Model()
materials = openmc.Materials.from_xml('../msbr/msbr-materials.xml')
fuel = materials[0]
fuel.add_nuclide('U233',0.025,'wo')
model.materials = openmc.Materials([fuel])

bottom, top = [openmc.ZPlane(z0 = v, boundary_type = 'reflective') for v in [-1000,1000]] 
cyl = openmc.ZCylinder(r=900,boundary_type = 'reflective')
cell = openmc.Cell(name = 'core', fill = fuel, region= -cyl & +bottom & -top)
uni = openmc.Universe(cells = [cell])
model.geometry.root_universe = uni

model.settings.particles = 1000
model.settings.batches = 50
model.settings.inactive = 25
model.settings.source = openmc.IndependentSource(space=openmc.stats.Box([-900, -900, -1000], 
                                                                        [900, 900, 1000]), constraints = {'fissionable':True})

operator = openmc.deplete.CoupledOperator(model, 'chain_endfb71_pwr.xml')
integrator = openmc.deplete.CECMIntegrator(operator=operator, timesteps=[15 for n in range(1,21)], power=3e9/4)

integrator.integrate(output=True)