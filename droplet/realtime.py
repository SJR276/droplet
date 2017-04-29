import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from droplet.dla import DiffusionLimitedAggregate2D

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
        assert isinstance(aggregate, DiffusionLimitedAggregate2D)
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
            self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=100,
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
