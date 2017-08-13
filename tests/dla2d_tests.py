import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate2d
from droplet.realtime import RealTimeAggregate2D

def point_attractor_test(nparticles, lattice_type, stickiness=1.0):
    """Generate an aggregate of `nparticles` on a specified lattice with
    a single point attractor as the initial seed.

    Parameters:
    -----------
    nparticles -- Number of particles to generate.
    lattice_type -- Type of lattice.
    stickiness -- Stickiness value of the aggregate [default 1.0].
    """
    point_agg = drp.Aggregate2D(stickiness=stickiness,
                                lattice_type=lattice_type)
    point_agg.generate(nparticles)
    plot_aggregate2d(point_agg, scalefactor=2.5)
    #print("Fractal dimension = {}".format(point_agg.fractal_dimension()))

def line_attractor_test(nparticles, lattice_type, attparticles, stickiness=1.0):
    """Generate an aggregate of `nparticles` on a specified lattice with
    a line of `attparticles` in size as the initial seed.

    Parameters:
    -----------
    nparticles -- Number of particles to generate.
    lattice_type -- Type of lattice.
    stickiness -- Stickiness value of the aggregate [default 1.0].
    """
    line_agg = drp.Aggregate2D(stickiness=stickiness,
                               lattice_type=lattice_type,
                               attractor_type=drp.AttractorType.LINE)
    line_agg.attractor_size = attparticles
    line_agg.generate(nparticles)
    plot_aggregate2d(line_agg)

def circle_attractor_test(nparticles, lattice_type, attradius, stickiness=1.0):
    """Generate an aggregate of `nparticles` on a specified lattice with
    a circle of `attradius` in size as the initial seed.

    Parameters:
    -----------
    nparticles -- Number of particles to generate.
    lattice_type -- Type of lattice.
    stickiness -- Stickiness value of the aggregate [default 1.0].
    """
    circle_agg = drp.Aggregate2D(stickiness=stickiness,
                                 lattice_type=lattice_type,
                                 attractor_type=drp.AttractorType.CIRCLE)
    circle_agg.attractor_size = attradius
    circle_agg.generate(nparticles)
    plot_aggregate2d(circle_agg)

def real_time_test(nparticles, lattice_type, stickiness=1.0, save=False, blitting=True,
                   filename=None):
    """Generates an aggregate of `nparticles` in real-time on a specified lattice
    with a single point attractor as the initial seed.

    Parameters:
    -----------
    nparticles -- Number of particles to generate.
    lattice_type -- Type of lattice.
    stickiness -- Stickiness value of the aggregate [default 1.0].
    save -- Determines whether to save the simulation to a file with
    name and extension specified by `filename`.
    blitting -- Determines whether to perform blitting for improved real-time
    rendering performance.
    filename -- Name and extension of file if saving the simulation.

    Returns:
    --------
    The handle to the simulation instance.
    """
    point_agg_rt = drp.Aggregate2D(stickiness=stickiness,
                                   lattice_type=lattice_type)
    sim = RealTimeAggregate2D(point_agg_rt, nparticles, save=save, blitting=blitting,
                              filename=filename)
    return sim

point_attractor_test(2000, drp.LatticeType.TRIANGLE)
#line_attractor_test(1000, drp.LatticeType.SQUARE, 20)
#circle_attractor_test(1000, drp.LatticeType.SQUARE, 10)
#real_time_test(1000, drp.LatticeType.SQUARE)
