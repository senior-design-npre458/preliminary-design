import openmc
import openmc.deplete

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

model.settings.particles = 10000
model.settings.batches = 100
model.settings.inactive = 50
model.settings.source = openmc.IndependentSource(space=openmc.stats.Box([-900, -900, -1000], 
                                                                        [900, 900, 1000]), constraints = {'fissionable':True})

operator = openmc.deplete.CoupledOperator(model, 'chain_endfb71_pwr.xml')
integrator = openmc.deplete.CECMIntegrator(operator=operator, timesteps=[10 for n in range(1,61)], power=1e9)

integrator.integrate(output=False)