import sys
sys.path.append("../")
import numpy as np
import matplotlib.pyplot as plt
import droplet as drp

def moving_average(data, period):
    assert isinstance(period, int)
    size = (int)(len(data)/period)
    mvavg = np.zeros((size, 2))
    mvavg[0][0] = 0
    mvavg[0][1] = np.ma.mean(data[:period])
    for idx in np.arange(1, size):
        mvavg[idx][0] = idx*period
        mvavg[idx][1] = mvavg[idx-1][1] + (data[idx*period] - data[(idx-1)*period])/period
    return mvavg

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

def combined_test(nparticles, scalefactor=2.0, save=False, filename=None, plot_mas=True):
    aggregate = drp.DiffusionLimitedAggregate2D(lattice_type=drp.LatticeType.SQUARE)
    aggregate.generate(nparticles)
    prange = np.arange(nparticles)
    fig = plt.figure(figsize=(14, 7))
    figdims = [(2, 2, 1), (2, 2, 3), (2, 2, (2, 4))]
    for row, col, plotno in figdims:
        sub = fig.add_subplot(row, col, plotno)
        if plotno == 1:
            sub.plot(prange, aggregate.required_steps)
            if plot_mas:
                rqd_steps_ma = moving_average(aggregate.required_steps, (int)(nparticles/100))
                sub.plot(rqd_steps_ma[:, 0], rqd_steps_ma[:, 1], 'g')
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Lattice Steps to Stick')
        elif plotno == 3:
            sub.plot(prange, aggregate.boundary_collisions, 'r')
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Boundary Collisions')
        else:
            max_x = np.max(aggregate.x_coords)
            max_y = np.max(aggregate.y_coords)
            sub.set_xlim(-max_x*scalefactor, max_x*scalefactor)
            sub.set_ylim(-max_y*scalefactor, max_y*scalefactor)
            sub.scatter(aggregate.x_coords, aggregate.y_coords, c=aggregate.colors,
                        s=4*np.pi)
            sub.set_xlabel('x')
            sub.set_ylabel('y')
    fig.show()
    if save:
        fig.savefig(filename)

combined_test(500, save=False, filename="../example_images/agg2dstats.png")
