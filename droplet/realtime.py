import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from droplet.dla import DiffusionLimitedAggregate2D

class RealTimeAggregate2D(object):
    """A real-time scatter plot of a two-dimensional Diffusion Limited
    Aggregate rendered using `matplotlib.animation.FuncAnimation`.
    """
    def __init__(self, aggregate, nparticles, blitting=True):
        """Creates a `RealTimeAggregate2D` instance from an existing
        `DiffusionLimitedAggregate2D` object.

        Parameters:
        -----------
        aggregate -- Argument of type `DiffusionLimitedAggregate2D` to use
        for generating the specific aggregate type.
        nparticles -- Number of particles to generate.
        blitting -- Determines whether `FuncAnimation` performs blitting for
        improved performance.
        """
        assert isinstance(aggregate, DiffusionLimitedAggregate2D)
        self.numparticles = nparticles
        self.stream = aggregate.generate_stream(nparticles)
        self.fig, self.ax = plt.subplots()
        self.scat = None
        self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=5,
                                           init_func=self.initialise_plot, blit=blitting)
    def initialise_plot(self):
        """Initialises the scatter plot using pre-specified chart properties.
        This function is used for the `init_func` argument of `FuncAnimation`.

        Returns:
        --------
        Sequence of scatter plots.
        """
        agg, col, count = next(self.stream)
        area = np.pi*25
        self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1],
                                    c=col[:count], s=area, animated=True)
        self.ax.axis([-40, 40, -40, 40])
        return self.scat,
    def update_plot(self, _):
        """Updates the scatter plot using the most recent yielded values from
        the aggregate stream generator function.

        Returns:
        --------
        Sequence of modified scatter plots.
        """
        agg, col, count = next(self.stream)
        data = np.hstack((agg[:count, np.newaxis], agg[:count, np.newaxis]))
        self.scat.set_offsets(data)
        #self.scat.set_array(col[:count])
        self.scat.set_color(col)
        return self.scat,
    def display(self):
        """Shows the real-time scatter plot."""
        plt.show()
