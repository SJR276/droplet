import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import droplet as drp

def plot_aggregate2d(aggregate, prad=2, edgecolors='none', alpha=1.0):
    """Plots a two-dimensional Diffusion Limited Aggregate on a scatter
    chart with the specified properties.

    Parameters:
    -----------
    aggregate -- The aggregate to plot.
    prad -- Radius of particles.
    edgecolors -- Color profile of particle edges.
    alpha -- Alpha value for particle transparency.

    Returns:
    --------
    A tuple of the figure, axes handles for the plot.
    """
    assert isinstance(aggregate, drp.DiffusionLimitedAggregate2D)
    agg_x = aggregate.x_coords
    agg_y = aggregate.y_coords
    color = aggregate.colors
    parea = np.pi*(prad)**2
    aggsz = len(agg_x)
    fig, axes = plt.subplots()
    axes.set_xlim(-aggsz/10, aggsz/10)
    axes.set_ylim(-aggsz/10, aggsz/10)
    axes.scatter(agg_x, agg_y, c=color, s=parea, edgecolors=edgecolors,
                 alpha=alpha)
    fig.show()
    return fig, axes

def plot_aggregate3d(aggregate, prad=2, edgecolors='none', alpha=0.7):
    assert isinstance(aggregate, drp.DiffusionLimitedAggregate3D)
    agg_x = aggregate.x_coords
    agg_y = aggregate.y_coords
    agg_z = aggregate.z_coords
    color = aggregate.colors
    parea = np.pi*prad*prad
    aggsz = len(agg_x)
    fig = plt.figure()
    axes = fig.add_subplot(111, projection='3d')
    axes.set_xlim(-aggsz/10, aggsz/10)
    axes.set_ylim(-aggsz/10, aggsz/10)
    axes.set_zlim(-aggsz/10, aggsz/10)
    axes.scatter(agg_x, agg_y, agg_z, c=color, s=parea, edgecolors=edgecolors,
                 alpha=alpha)
    fig.show()
    return fig, axes
