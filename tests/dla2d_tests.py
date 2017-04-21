import sys
sys.path.append("../")
import numpy as np
import droplet as drp
from droplet.plotting import plot_2d_aggregate
import matplotlib.pyplot as plt

def simple_test(nparticles):
    dla_2d = drp.DiffusionLimitedAggregate2D()
    dla_2d.generate(nparticles)
    plot_2d_aggregate(dla_2d)

simple_test(500)
