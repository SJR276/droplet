import sys
sys.path.append("../")
import numpy as np
import matplotlib.pyplot as plt
import droplet as drp

def steps_to_stick_test(nparticles):
    aggregate = drp.DiffusionLimitedAggregate2D(lattice_type=drp.LatticeType.SQUARE)
    aggregate.generate(nparticles)
    fig, axes = plt.subplots()
    prange = np.arange(nparticles)
    axes.plot(prange, aggregate.required_steps)
    axes.set_xlabel('Aggregate Particle Index')
    axes.set_ylabel('Lattice Steps to Stick')
    fig.show()

def boundary_collisions_test(nparticles):
    aggregate = drp.DiffusionLimitedAggregate2D()
    aggregate.generate(nparticles)
    fig, axes = plt.subplots()
    prange = np.arange(nparticles)
    axes.plot(prange, aggregate.boundary_collisions)
    axes.set_xlabel('Aggregate Particle Index')
    axes.set_ylabel('Boundary Collsions')
    fig.show()

def combined_test(nparticles, save=False, filename=None):
    aggregate = drp.DiffusionLimitedAggregate2D()
    aggregate.generate(nparticles)
    prange = np.arange(nparticles)
    fig = plt.figure(figsize=(14,7))
    figdims = [(2,2,1), (2,2,3), (2,2,(2,4))]
    count = 0
    for nrows, ncols, pn in figdims:
        sub = fig.add_subplot(nrows, ncols, pn)
        if count == 0:
            sub.plot(prange, aggregate.required_steps)
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Lattice Steps to Stick')
        elif count == 1:
            sub.plot(prange, aggregate.boundary_collisions, 'r')
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Boundary Collisions')
        else:
            sub.set_xlim(-nparticles/10, nparticles/10)
            sub.set_ylim(-nparticles/10, nparticles/10)
            sub.scatter(aggregate.x_coords, aggregate.y_coords, c=aggregate.colors,
                        s=4*np.pi)
            sub.set_xlabel('x')
            sub.set_ylabel('y')
        count += 1
    fig.show()
    fig.savefig(filename)

combined_test(500, save=True, filename="../example_images/agg2dstats.png")
