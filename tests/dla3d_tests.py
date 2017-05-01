import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate3d

def simple_test(nparticles):
    aggregate = drp.DiffusionLimitedAggregate3D()
    aggregate.generate(nparticles)
    plot_aggregate3d(aggregate)

simple_test(500)
