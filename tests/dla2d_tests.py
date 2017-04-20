import sys
sys.path.append("../")
import numpy as np
import droplet as drp
import matplotlib.pyplot as plt

def simple_test(nparticles, particle_radius):
    dla_2d = drp.DiffusionLimitedAggregate2D(1.0)
    agg, col = dla_2d.generate(nparticles)
    fig, axes = plt.subplots()
    axes.scatter(agg[:,0], agg[:,1], c=col, s=np.pi*(particle_radius)**2)
    fig.show()

simple_test(500, 5)
