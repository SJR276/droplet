import sys
sys.path.append("../")
import numpy as np
import droplet as drp
from droplet.plotting import plot_2d_aggregate
from droplet.realtime import RealTimeAggregate2D
import matplotlib.pyplot as plt

def simple_test(nparticles):
    dla_2d = drp.DiffusionLimitedAggregate2D()
    dla_2d.generate(nparticles)
    plot_2d_aggregate(dla_2d)

def real_time_test(nparticles):
    dla2d = drp.DiffusionLimitedAggregate2D(stickiness=1.0, lattice_type=drp.LatticeType.SQUARE)
    sim = RealTimeAggregate2D(dla2d, nparticles, save=True, blitting=True,
                              filename='../example_images/agg2dtest.gif')

real_time_test(500)
