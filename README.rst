droplet
=======

Python toolkit for creating and manipulating diffusion limited aggregate structures. 

*Note that droplet is still in the early stages of development, support for the features and installation steps shown below will be added shortly.*

Features
--------

droplet is a Python based simulation suite which allows creation and manipulation of Diffusion Limited Aggregates (DLAs) in both real-time and otherwise. An incomplete featue list of droplet follows:

* Fast and accurate aggregate collision detection with support for varying stickiness structures
* Different lattice geometries such as square or triangular in both 2D and 3D
* Support for a variety of initial attractor seeds including points, circles and spheres
* Real-time visualisation of aggregate clustering using `matplotlib.animation`.
* Easy, single step installation via PyPI using: `pip install droplet`
* Fully open-source with all code available at https://github.com/SJR276/droplet
* No complicated dependencies required

Single-Step Installation
------------------------

Installation of droplet requires only a single step with pip::

    pip install droplet

Then you can execute a simple real-time droplet simulation, such as

.. code:: python

    import droplet as drp
    aggregate = drp.DiffusionLimitedAggregate2D()
    sim = drp.RealTimeAggregate2D(aggregate, nparticles=1000)

Examples
--------

The following simple case simulates a 2D DLA of 500 particles on a square-lattice in real-time, saving the animated plot to an output file:

.. code:: python

    import droplet as drp
    aggregate = drp.Aggregate2D()
    sim = drp.RealTimeAggregate2D(aggregate, nparticles=500, save=True,
                                  filename="../example_images/agg2dtest.gif")

This produces the animated scatter-chart shown below, where the colour gradient represents the order at which particles were added to the aggregate.

.. image:: example_images/agg2dtest.gif 

Three-dimensional aggregates can also be simulated in real-time using similar syntax. The code shown below produces an aggregate on a cubic lattice with the simulation again saved to an output file:

.. code:: python

    import droplet as drp
    aggregate = drp.Aggregate3D()
    sim = drp.RealTimeAggregate3D(aggregate, nparticles=200, autorotate=True, save=True,
                                  filename="../example_images/agg3dtest.gif")

A gif of the resulting animated scatter-chart is shown below.

.. image:: example_images/agg3dtest.gif

Statistics describing the generation of the aggregate can be tracked and plotted, the following example shows the number of lattice steps and boundary collisions experienced by each Browian particle before it stuck to the aggregate for a triangular lattice.

.. code:: python

    import numpy as np
    import matplotlib.pyplot as plt
    import droplet as drp

    nparticles = 1000
    aggregate = drp.Aggregate2D(drp.LatticeType.TRIANGLE)
    aggregate.generate(nparticles)
    prange = np.arange(nparticles)
    fig = plt.figure()
    # dimensions of subplots for figure
    figdims = [(2,2,1), (2,2,3), (2,2,(2,4))]
    for row, col, plotno in figdims:
        sub = fig.add_subplot(row, col, plotno)
        # plot required steps for each particle
        if plotno == 1:
            sub.plot(prange, aggregate.required_steps, 'b',
                     label=r"Required steps")
            # period-10 simple moving average
            rqd_steps_ma = simple_moving_average(aggregate.required_steps, 10)
            sub.plot(rqd_steps_ma[:, 0], rqd_steps_ma[:, 1], 'r',
                     label=r"10 particle SMA")
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Lattice Steps to Stick')
            sub.legend()
        # plot boundary collisions for each particle
        elif plotno == 3:
            sub.plot(prange, aggregate.boundary_collisions, 'g',
                     label=r"Boundary collisions")
            bcoll_ma = simple_moving_average(aggregate.boundary_collisions, 10)
            sub.plot(bcoll_ma[:, 0], bcoll_ma[:, 1], 'r',
                     label=r"10 particle SMA")
            sub.set_xlabel('Aggregate Particle Index')
            sub.set_ylabel('Boundary Collisions')
            sub.legend()
        # plot aggregate itself
        else:
            agg = aggregate.as_ndarray()
            max_x = aggregate.max_x
            max_y = aggregate.max_y
            sf = 3.0 # viewing scale-factor
            sub.set_xlim(-max_x*sf, max_x*sf)
            sub.set_ylim(-max_y*sf, max_y*sf)
            sub.scatter(agg[:, 0], agg[:, 1], c=aggregate.colors,
                        s=4*np.pi)
            sub.set_xlabel('x')
            sub.set_ylabel('y')
    fig.show()

From this example, the figure below is produced.

.. image:: example_images/agg2dstats.png
