import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from droplet.dla import DiffusionLimitedAggregate2D

class RealTimeAggregate2D(object):
    """A real-time scatter plot of a two-dimensional Diffusion Limited
    Aggregate rendered using `matplotlib.animation.FuncAnimation`.
    """
    def __init__(self, aggregate, nparticles, blitting=False):
        assert isinstance(aggregate, DiffusionLimitedAggregate2D)
        self.numparticles = nparticles
        self.stream = aggregate.generate_stream(nparticles)
        self.fig, self.ax = plt.subplots()
        self.sim = animation.FuncAnimation(self.fig, self.update_plot, interval=5,
                                           init_func=self.initialise_plot, blit=blitting)
    def initialise_plot(self):
        agg, col, count = next(self.stream)
        area = np.pi*25
        self.scat = self.ax.scatter(agg[:count, 0], agg[:count, 1],
                                    c=col[:count], s=area, animated=True)
        self.ax.axis([-50, 50, -50, 50])
        return self.scat,
    def update_plot(self, _):
        agg, col, count = next(self.stream)
        data = np.hstack((agg[:count, 0], agg[:count, 1]))
        self.scat.set_offsets(data)
        self.scat._sizes = np.pi*25
        self.scat.set_array(col[:count])
        return self.scat,
    def display(self):
        plt.show()
