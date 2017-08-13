import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import droplet as drp

def plot_aggregate2d(aggregate, prad=2, edgecolors='none', alpha=1.0,
                     scalefactor=1.5):
    """Plots a two-dimensional Diffusion Limited Aggregate on a
    scatter chart with the specified properties.

    Parameters
    ----------
    *aggregate* :: `droplet.Aggregate2D`

        The aggregate to plot.

    *prad* :: `float`, optional, default = 2

        Visual radius of particles.

    *edgecolors* :: `color` or sequence of `color`, optional, default = 'none'

        Color profile of particle edges.

    *alpha* :: `float`, optional, default = 1.0

        Alpha value for particle opacity.

    *scalefactor* :: `float`, optional, default = 1.5

        Viewing scale factor, a floating-point multiple
        of the maximum (x,y) dimensions of the aggregate.

    Returns
    -------
    A tuple of the figure, axes handles for the plot.
    """
    assert isinstance(aggregate, drp.Aggregate2D)
    agg = aggregate.as_ndarray()
    max_x = aggregate.max_x
    max_y = aggregate.max_y
    color = aggregate.colors
    parea = np.pi*prad*prad
    fig, axes = plt.subplots()
    axes.set_xlim(-max_x*scalefactor, max_x*scalefactor)
    axes.set_ylim(-max_y*scalefactor, max_y*scalefactor)
    axes.scatter(agg[:, 0], agg[:, 1], c=color, s=parea, edgecolors=edgecolors,
                 alpha=alpha)
    fig.show()
    return fig, axes

def plot_aggregate3d(aggregate, prad=2, edgecolors='none', alpha=0.7,
                     scalefactor=1.5):
    """Plots a three-dimensional Diffusion Limited Aggregate on a
    scatter chart with the specified properties.

    Parameters
    ----------
    *aggregate* :: `droplet.Aggregate3D`

        The aggregate to plot.

    *prad* :: `float`, optional, default = 2

        Visual radius of particles.

    *edgecolors* :: `color` or sequence of `color`, optional, default = 'none'

        Color profile of particle edges.

    *alpha* :: `float`, optional, default = 0.7

        Alpha value for particle opacity.

    *scalefactor* :: `float`, optional, default = 1.5

        Viewing scale factor, a floating-point multiple
        of the maximum (x,y) dimensions of the aggregate.

    Returns
    -------
    A tuple of the figure, axes handles for the plot.
    """
    assert isinstance(aggregate, drp.Aggregate3D)
    agg = aggregate.as_ndarray()
    max_x = aggregate.max_x
    max_y = aggregate.max_y
    max_z = aggregate.max_z
    color = aggregate.colors
    parea = np.pi*prad*prad
    fig = plt.figure()
    axes = fig.add_subplot(111, projection='3d')
    axes.set_xlim(-max_x*scalefactor, max_x*scalefactor)
    axes.set_ylim(-max_y*scalefactor, max_y*scalefactor)
    axes.set_zlim(-max_z*scalefactor, max_z*scalefactor)
    axes.scatter(agg[:, 0], agg[:, 1], agg[:, 2], c=color, s=parea,
                 edgecolors=edgecolors, alpha=alpha)
    fig.show()
    return fig, axes

def plot_aggregate(aggregate, prad=2, edgecolors='none', alpha=1.0,
                   scalefactor=1.5):
    """Plots a  Diffusion Limited Aggregate on a scatter
    chart with the specified properties.

    Parameters
    ----------
    *aggregate* :: `droplet.Aggregate2D` or `droplet.Aggregate.3D`

        The aggregate to plot.

    *prad* :: `float`, optional, default = 2

        Visual radius of particles.

    *edgecolors* :: `color` or sequence of `color`, optional, default = 'none'

        Color profile of particle edges.

    *alpha* :: `float`, optional, default = 1.0

        Alpha value for particle opacity.

    *scalefactor* :: `float`, optional, default = 1.5

        Viewing scale factor, a floating-point multiple
        of the maximum (x,y) dimensions of the aggregate.

    Returns
    -------
    A tuple of the figure, axes handles for the plot.
    """
    if isinstance(aggregate, drp.Aggregate2D):
        return plot_aggregate2d(aggregate, prad=prad,
                                edgecolors=edgecolors,
                                alpha=alpha,
                                scalefactor=scalefactor)
    elif isinstance(aggregate, drp.Aggregate3D):
        return plot_aggregate3d(aggregate, prad=prad,
                                edgecolors=edgecolors,
                                alpha=alpha,
                                scalefactor=scalefactor)
