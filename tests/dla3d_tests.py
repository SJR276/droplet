import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate3d
from droplet.realtime import RealTimeAggregate3D

def simple_test(nparticles):
    aggregate = drp.DiffusionLimitedAggregate3D(lattice_type=drp.LatticeType.TRIANGLE)
    aggregate.generate(nparticles)
    plot_aggregate3d(aggregate)

def real_time_test(nparticles):
    aggregate = drp.DiffusionLimitedAggregate3D()
    sim = RealTimeAggregate3D(aggregate, nparticles, blitting=True)

simple_test(500)
#real_time_test(500)
