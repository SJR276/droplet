import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate2d
from droplet.realtime import RealTimeAggregate2D

def simple_test(nparticles):
    dla_2d = drp.DiffusionLimitedAggregate2D()
    dla_2d.generate(nparticles)
    plot_aggregate2d(dla_2d)

def real_time_test(nparticles):
    dla2d = drp.DiffusionLimitedAggregate2D(stickiness=1.0, lattice_type=drp.LatticeType.TRIANGLE)
    sim = RealTimeAggregate2D(dla2d, nparticles, save=False, blitting=True,
                              filename='../example_images/agg2dtest.gif')

real_time_test(500)
