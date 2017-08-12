import sys
sys.path.append("../")
import numpy as np
import matplotlib.pyplot as plt
import droplet as drp

def simple_moving_average(data, period):
    """Computes the simple moving average (SMA) of an `np.array`
    of data using a specified period. The `data` can be either
    one or two-dimensional, in both cases a two-dimensional `np.array`
    is returned where the first dimension contains:

    - a sequence of `[period, 2*period, 3*period, ..., ]` if `data` is
    one-dimensional or,
    - a sequence of `[data[period][0], data[2*period][0], data[3*period][0], ..., ]` if
    `data` is two-dimensional.

    Parameters:
    -----------
    data -- An `np.array` of data for which to compute the simple moving average. Must
    be either 1D or 2D, in the latter case the SMA of the second dimension will be calculated.
    period -- An integer representing the data indexing period.

    Returns:
    --------
    A 2D `np.array` where the second dimension contains SMA values computed for each period
    indexed in the first dimension.
    """
    assert isinstance(period, int)
    invp = 1/period # for optimisation
    size = (int)(len(data)*invp)
    sma = np.zeros((size, 2))
    datadims = 0
    try: # determining dimensions of data
        temp = data.shape[1]
        if temp == 1:
            sma[0][0] = period
            datadims = 1
        elif temp == 2:
            sma[0][0] = data[period][0]
            datadims = 2
        else: # raise exception when data dimensions > 2
            raise TypeError("data array must be one or two dimensional.")
    except IndexError:
        sma[0][0] = period
        datadims = 1
    if datadims == 1:
        sma[0][1] = np.ma.mean(data[:period])
    elif datadims == 2:
        sma[0][1] = np.ma.mean(data[:period, 1])
    for idx in np.arange(1, size):
        if datadims == 1:
            sma[idx][0] = (idx+1)*period
            sma[idx][1] = sma[idx-1][1] + (data[idx*period] - data[(idx-1)*period])*invp
        elif datadims == 2:
            sma[idx][0] = data[(idx+1)*period][0]
            sma[idx][1] = sma[idx-1][1] + (data[idx*period][1] - data[(idx-1)*period][1])*invp
    return sma

def steps_to_stick_test(nparticles):
    aggregate = drp.Aggregate2D()
    aggregate.generate(nparticles)
    fig, axes = plt.subplots()
    prange = np.arange(nparticles)
    axes.plot(prange, aggregate.required_steps)
    axes.set_xlabel('Aggregate Particle Index')
    axes.set_ylabel('Lattice Steps to Stick')
    fig.show()

def boundary_collisions_test(nparticles):
    aggregate = drp.Aggregate2D()
    aggregate.generate(nparticles)
    fig, axes = plt.subplots()
    prange = np.arange(nparticles)
    axes.plot(prange, aggregate.boundary_collisions)
    axes.set_xlabel('Aggregate Particle Index')
    axes.set_ylabel('Boundary Collsions')
    fig.show()

def combined_test(nparticles, scalefactor=3.0, save=False, filename=None, plot_sma=True,
                  sma_period=None):
    aggregate = drp.Aggregate2D(lattice_type=drp.LatticeType.SQUARE)
    aggregate.generate(nparticles)
    prange = np.arange(nparticles)
    fig = plt.figure(figsize=(14, 7))
    figdims = [(2, 2, 1), (2, 2, 3), (2, 2, (2, 4))]
    for row, col, plotno in figdims:
        sub = fig.add_subplot(row, col, plotno)
        if plotno == 1:
            sub.plot(prange, aggregate.required_steps)
            if plot_sma:
                rqd_steps_ma = simple_moving_average(aggregate.required_steps, sma_period)
                sub.plot(rqd_steps_ma[:, 0], rqd_steps_ma[:, 1], 'g')
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Lattice Steps to Stick')
        elif plotno == 3:
            sub.plot(prange, aggregate.boundary_collisions, 'r')
            if plot_sma:
                bcoll_ma = simple_moving_average(aggregate.boundary_collisions, sma_period)
                sub.plot(bcoll_ma[:, 0], bcoll_ma[:, 1], 'g')
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Boundary Collisions')
        else:
            agg = aggregate.as_ndarray()
            max_x = aggregate.max_x
            max_y = aggregate.max_y
            sub.set_xlim(-max_x*scalefactor, max_x*scalefactor)
            sub.set_ylim(-max_y*scalefactor, max_y*scalefactor)
            sub.scatter(agg[:, 0], agg[:, 1], c=aggregate.colors,
                        s=4*np.pi)
            sub.set_xlabel('x')
            sub.set_ylabel('y')
    fig.show()
    if save:
        fig.savefig(filename)

combined_test(1000, save=False, filename="../example_images/agg2dstats.png", sma_period=10)
