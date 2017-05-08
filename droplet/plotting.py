import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import droplet as drp

def plot_aggregate2d(aggregate, prad=2, edgecolors='none', alpha=1.0,
                     inv_zoom=1.5):
    """Plots a two-dimensional Diffusion Limited Aggregate on a scatter
    chart with the specified properties.

    Parameters:
    -----------
    aggregate -- The aggregate to plot.
    prad -- Radius of particles.
    edgecolors -- Color profile of particle edges.
    alpha -- Alpha value for particle transparency.
    inv_zoom -- Inverse zoom scaling.

    Returns:
    --------
    A tuple of the figure, axes handles for the plot.
    """
    assert isinstance(aggregate, drp.DiffusionLimitedAggregate2D)
    agg_x = aggregate.x_coords
    agg_y = aggregate.y_coords
    color = aggregate.colors
    parea = np.pi*prad*prad
    fig, axes = plt.subplots()
    max_x = np.max(agg_x)
    max_y = np.max(agg_y)
    axes.set_xlim(-max_x*inv_zoom, max_x*inv_zoom)
    axes.set_ylim(-max_y*inv_zoom, max_y*inv_zoom)
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
    axes.set_xlim(-aggsz/20, aggsz/20)
    axes.set_ylim(-aggsz/20, aggsz/20)
    axes.set_zlim(-aggsz/20, aggsz/20)
    axes.scatter(agg_x, agg_y, agg_z, c=color, s=parea, edgecolors=edgecolors,
                 alpha=alpha)
    fig.show()
    return fig, axes

def plot_aggregate(aggregate, prad=2, edgecolors='none', alpha=1.0):
    if isinstance(aggregate, drp.DiffusionLimitedAggregate2D):
        return plot_aggregate2d(aggregate, prad=prad,
                                edgecolors=edgecolors, alpha=alpha)
    elif isinstance(aggregate, drp.DiffusionLimitedAggregate3D):
        return plot_aggregate3d(aggregate, prad=prad,
                                edgecolors=edgecolors, alpha=alpha)
