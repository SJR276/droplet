import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate3d
from droplet.realtime import RealTimeAggregate3D

def simple_test(nparticles):
    aggregate = drp.Aggregate3D(lattice_type=drp.LatticeType.TRIANGLE)
    aggregate.generate(nparticles)
    plot_aggregate3d(aggregate)

def real_time_test(nparticles):
    aggregate = drp.Aggregate3D(lattice_type=drp.LatticeType.SQUARE)
    sim = RealTimeAggregate3D(aggregate, nparticles, blitting=True, save=False,
                              filename="../example_images/agg3dtest.gif", autorotate=False)

#simple_test(1000)
real_time_test(200)
