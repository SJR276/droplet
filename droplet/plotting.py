import numpy as np
import matplotlib.pyplot as plt
import droplet as drp

def plot_2d_aggregate(aggregate, prad=5, edgecolors='none', alpha=1.0):
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
    fig, axes = plt.subplots()
    axes.scatter(agg_x, agg_y, c=color, s=parea, edgecolors=edgecolors,
                 alpha=alpha)
    fig.show()
    return fig, axes
