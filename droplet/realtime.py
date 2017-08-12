import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from droplet.dla import DiffusionLimitedAggregate2D
from droplet.dla import DiffusionLimitedAggregate3D

class RealTimeAggregate2D(object):
    """A real-time scatter plot of a two-dimensional Diffusion Limited
    Aggregate rendered using `matplotlib.animation.FuncAnimation`.
    """
    def __init__(self, aggregate, nparticles, blitting=True, save=False,
                 filename=None, writer='imagemagick', prad=2):
        """Creates a `RealTimeAggregate2D` instance from an existing
        `DiffusionLimitedAggregate2D` object.

        Parameters:
        -----------
        aggregate -- Argument of type `DiffusionLimitedAggregate2D` to use
        for generating the specific aggregate type.
        nparticles -- Number of particles to generate.
        blitting -- Determines whether `FuncAnimation` performs blitting for
        improved performance.
        save -- If `True` saves the animated simulation to a file with name
        and extension specified by `filename`. Otherwise, displays the plot
        in real-time to the screen.
        filename -- Name, and extension, of file to write to if `save == True`.
        writer -- Type of writer to user for saving if `save == True`, defaults
        to `imagemagick`.
        """
        #assert isinstance(aggregate, DiffusionLimitedAggregate2D)
        self.numparticles = nparticles
        self.prad = prad
        self.stream = aggregate.generate_stream(nparticles)
        self.fig, self.ax = plt.subplots()
        if save:
            agg, col, count = next(self.stream)
            area = np.pi*(self.prad*self.prad)
            self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1],
                                        c=col, s=area, animated=True)
            axlims = nparticles/10
            if axlims < 30:
                axlims = 30
            self.ax.axis([-axlims, axlims, -axlims, axlims])
            self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=50,
                                               blit=False, frames=nparticles)
            self.sim.save(filename, writer)
        else:
            self.scat = None
            self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=10,
                                               init_func=self.initialise_plot,
                                               blit=blitting)
            plt.show()
    def initialise_plot(self):
        """Initialises the scatter plot using pre-specified chart properties.
        This function is used for the `init_func` argument of `FuncAnimation`.

        Returns:
        --------
        Sequence of scatter plots.
        """
        try:
            agg, col, count = next(self.stream)
            area = np.pi*(self.prad*self.prad)
            self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1],
                                        c=col, s=area, animated=True)
            axlims = self.numparticles/10
            if axlims < 30:
                axlims = 30
            self.ax.axis([-axlims, axlims, -axlims, axlims])
        except StopIteration:
            pass
        finally:
            return self.scat,
    def update_plot(self, _):
        """Updates the scatter plot using the most recent yielded values from
        the aggregate stream generator function.

        Returns:
        --------
        Sequence of modified scatter plots.
        """
        try:
            agg, col, count = next(self.stream)
            data = np.hstack((agg[:count, np.newaxis], agg[:count, np.newaxis]))
            self.scat.set_offsets(data)
        except StopIteration:
            pass
        finally:
            return self.scat,

class RealTimeAggregate3D(object):
    """A real-time scatter plot of a three-dimensional Diffusion Limited
    Aggregate rendered using `matplotlib.animation.FuncAnimation`.
    """
    def __init__(self, aggregate, nparticles, blitting=True, save=False,
                 filename=None, writer='imagemagick', prad=2, autorotate=False):
        """Creates a `RealTimeAggregate3D` instance from an existing
        `DiffusionLimitedAggregate3D` object.

        Parameters:
        -----------
        aggregate -- Argument of type `DiffusionLimitedAggregate3D` to use
        for generating the specific aggregate type.
        nparticles -- Number of particles to generate.
        blitting -- Determines whether `FuncAnimation` performs blitting for
        improved performance.
        save -- If `True` saves the animated simulation to a file with name
        and extension specified by `filename`. Otherwise, displays the plot
        in real-time to the screen.
        filename -- Name, and extension, of file to write to if `save == True`.
        writer -- Type of writer to use for saving, defaults to `imagemagick`.
        """
        assert isinstance(aggregate, DiffusionLimitedAggregate3D)
        self.numparticles = nparticles
        self.prad = prad
        self.angle = 0
        self.autorotate = autorotate
        self.stream = aggregate.generate_stream(nparticles)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        if save:
            agg, col, count = next(self.stream)
            area = np.pi*(self.prad*self.prad)
            self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1], agg[:count, 2],
                                        c=col, s=area, animated=True)
            axlims = self.numparticles/25
            if axlims < 10:
                axlims = 10
            self.ax.set_xlim(-axlims, axlims)
            self.ax.set_ylim(-axlims, axlims)
            self.ax.set_zlim(-axlims, axlims)
            self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=50,
                                               blit=False, frames=nparticles)
            self.sim.save(filename, writer)
        else:
            self.scat = None
            self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=10,
                                               init_func=self.initialise_plot, blit=blitting)
            plt.show()
    def initialise_plot(self):
        """Initialises the scatter plot using pre-specified chart properties. This
        function is used for the `init_func` argument of `FuncAnimation`.

        Returns:
        --------
        Sequence of scatter plots.
        """
        try:
            agg, col, count = next(self.stream)
            area = np.pi*(self.prad*self.prad)
            self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1], agg[:count, 2],
                                        c=col, s=area, animated=True)
            axlims = self.numparticles/25
            if axlims < 10:
                axlims = 10
            self.ax.set_xlim(-axlims, axlims)
            self.ax.set_ylim(-axlims, axlims)
            self.ax.set_zlim(-axlims, axlims)
        except StopIteration:
            pass
        finally:
            return self.scat,
    def update_plot(self, _):
        """Updates the scatter plot using the most recent yielded values from
        the aggregate stream generator function.

        Returns:
        --------
        Sequence of modified scatter plots.
        """
        try:
            agg, col, count = next(self.stream)
            self.scat._offsets3d = (agg[:count, 0], agg[:count, 1], agg[:count, 2])
            self.scat.set_facecolor(col)
            if self.autorotate:
                self.angle = (self.angle + 2)%360
                self.ax.view_init(30+self.angle, self.angle)
            plt.draw()
        except StopIteration:
            pass
        finally:
            return self.scat,
