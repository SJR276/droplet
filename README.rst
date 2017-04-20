droplet
=======

Python toolkit for creating and manipulating diffusion limited aggregate structures. NOTE THAT droplet IS STILL IN THE EARLY STAGES OF DEVELOPMENT, SUPPORT FOR THE FEATURES AND INSTALLATION STEPS SHOWN BELOW WILL BE ADDED SHORTLY.

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
    dla2d = drp.DiffusionLimitedAggregate2D(stickiness=1.0)
    dla2d.generate(nparticles=1000, real_time_display=True)