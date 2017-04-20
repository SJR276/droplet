from enum import Enum
import numpy as np
from numpy.random import rand
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import droplet.colorprofiles as clrpr
import droplet.external.progressbar as pb

class LatticeType(Enum):
    """The geometry of a lattice, determines the motion of particles."""
    SQUARE = 1
    TRIANGLE = 2

class AttractorType(Enum):
    """The initial attractor seed of an aggregate."""
    POINT = 1
    CIRCLE = 2
    SPHERE = 3
    LINE = 4
    PLANE = 5

class DiffusionLimitedAggregate2D(object):
    """A two-dimensional Diffusion Limited Aggregate (DLA) structure
    with associated properties such as the aggregate stickiness, the
    type of lattice and the type of attractor used.
    """
    def __init__(self, stickiness, lattice_type=LatticeType.SQUARE,
                 attractor_type=AttractorType.POINT):
        """Create a `DiffusionLimitedAggregate2D` instance with specified
        properties.

        Arguments:
        ----------
        - stickiness -- Floating point value in [0, 1] determining probability
        of a particle sticking to the aggregate upon collision.
        - lattice_type -- Type of lattice upon which to execute aggregate generation.
        - attractor_type -- Type of initial attractor seed.

        Exceptions:
        -----------
        - Raises `ValueError` if stickiness not in [0, 1].
        - Raises `ValueError` if attractor type set to a 3D geometry.
        """
        if stickiness < 0.0 or stickiness > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self.__stickiness = stickiness
        self.lattice_type = lattice_type
        if (attractor_type == AttractorType.SPHERE or
                attractor_type == AttractorType.PLANE):
            raise ValueError("Attractor type must be of a 2D topology for 2D aggregates")
        self.__attractor_type = attractor_type
        self.__aggregate = np.array(0)
        self.__colors = np.array(0)
        self.__attractor = np.array(0)
        self.attractor_size = 1
        self.__boundary_offset = 8
        self.__spawn_diam = self.__boundary_offset
        self.__max_radius_sqd = 0
    @property
    def stickiness(self):
        """Returns the stickiness property of the aggregate. This describes
        the probability of a particle sticking to the aggregate upon collision.

        Returns:
        --------
        The aggregate stickiness parameter.
        """
        return self.__stickiness
    @stickiness.setter
    def stickiness(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self.__stickiness = value
    @property
    def attractor_type(self):
        """Returns the type of the attractor used for the aggregate's initial seed.

        Returns:
        --------
        Type of attractor seed.
        """
        return self.__attractor_type
    @attractor_type.setter
    def attractor_type(self, value):
        if (value == AttractorType.SPHERE or
                value == AttractorType.PLANE):
            raise ValueError("Attractor type must be of a 2D topology for 2D aggregates")
        self.__attractor_type = value
    @property
    def x_coords(self):
        """Returns the x co-ordinates of all particles in the aggregate. This
        is a readonly property, useful for plotting.

        Returns:
        --------
        The x co-ordinates of the aggregate particles.
        """
        return self.__aggregate[:,0]
    @property
    def y_coords(self):
        """Returns the y co-ordinates of all particles in the aggregate. This
        is a readonly property, useful for plotting.

        Returns:
        --------
        The y co-ordinates of the aggregate particles.
        """
        return self.__aggregate[:,1]
    def __initialise_attractor(self):
        if self.__attractor_type == AttractorType.POINT:
            self.__attractor = np.zeros((1, 2))
            return np.arange(1)
        elif self.__attractor_type == AttractorType.LINE:
            self.__attractor = np.zeros((self.attractor_size, 2), dtype=int)
            self.__attractor[:,0] = (np.arange(self.attractor_size)
                                     - (int)(0.5*self.attractor_size))
            return np.arange(self.attractor_size)
    def __spawn_brownian_particle(self, crr_pos):
        ppr = rand()
        if self.__attractor_type == AttractorType.POINT:
            if ppr < 0.5:
                crr_pos[0] = self.__spawn_diam*(rand() - 0.5)
                if ppr < 0.25:
                    crr_pos[1] = self.__spawn_diam*0.5
                else:
                    crr_pos[1] = -self.__spawn_diam*0.5
            else:
                if ppr < 0.75:
                    crr_pos[0] = self.__spawn_diam*0.5
                else:
                    crr_pos[0] = -self.__spawn_diam*0.5
                crr_pos[1] = self.__spawn_diam*(rand() - 0.5)
    def __update_brownian_particle(self, crr_pos):
        mov_dir = rand()
        if self.lattice_type == LatticeType.SQUARE:
            if mov_dir < 0.25:
                crr_pos[0] += 1
            elif mov_dir >= 0.25 and mov_dir < 0.5:
                crr_pos[0] -= 1
            elif mov_dir >= 0.5 and mov_dir < 0.75:
                crr_pos[1] += 1
            else:
                crr_pos[1] -= 1
        elif self.lattice_type == LatticeType.TRIANGLE:
            if mov_dir < 1.0/6.0:
                crr_pos[0] += 1
            elif mov_dir >= 1.0/6.0 and mov_dir < 2.0/6.0:
                crr_pos[0] -= 1
            elif mov_dir >= 2.0/6.0 and mov_dir < 3.0/6.0:
                crr_pos[0] += 1
                crr_pos[1] += 1
            elif mov_dir >= 3.0/6.0 and mov_dir < 4.0/6.0:
                crr_pos[0] += 1
                crr_pos[1] -= 1
            elif mov_dir >= 4.0/6.0 and mov_dir < 5.0/6.0:
                crr_pos[0] -= 1
                crr_pos[1] -= 1
            else:
                crr_pos[0] -= 1
                crr_pos[1] += 1
    def __lattice_boundary_collision(self, crr_pos, prv_pos):
        epsilon = 2
        if self.__attractor_type == AttractorType.POINT:
            if (np.abs(crr_pos[0]) > (int)(self.__spawn_diam*0.5 + epsilon) or
                    np.abs(crr_pos[1]) > (int)(self.__spawn_diam*0.5 + epsilon)):
                crr_pos[:] = prv_pos
    def __push_to_aggregate(self, particle, count):
        self.__aggregate[count][0] = particle[0]
        self.__aggregate[count][1] = particle[1]
        radius_sqd = particle[0]**2 + particle[1]**2
        if radius_sqd > self.__max_radius_sqd:
            self.__max_radius_sqd = radius_sqd
            self.__spawn_diam = 2*(int)(np.sqrt(radius_sqd)) + self.__boundary_offset
    def __aggregate_collision(self, crr_pos, prv_pos, count, agg_range, att_range):
        """Checks for collision of a particle undergoing Brownian motion with
        the aggregate or attractor structure, and adds the particle to the
        aggregate if a collision does occur.

        Arguments:
        ----------
        crr_pos -- Current position of particle.
        prv_pos -- Previous position of particle.
        count -- Number of particles stuck to the aggregate.
        agg_range -- A `np.arange` array with a size corresponding to number of
        particles to generate.
        att_range -- A `np.arange` array with a size corresponding to the size of
        the attractor structure.

        Returns:
        --------
        `True` if a collision occurred, `False` otherwise.
        """
        if rand() > self.__stickiness:
            return False
        # check for collision with attractor seed
        for idx1 in att_range:
            if (self.__attractor[idx1][0] == crr_pos[0] and
                    self.__attractor[idx1][0] == crr_pos[1]):
                self.__push_to_aggregate(prv_pos, count)
                return True
        # check for collision with aggregate structure
        for idx2 in agg_range:
            if (self.__aggregate[idx2][0] == crr_pos[0] and
                    self.__aggregate[idx2][1] == crr_pos[1]):
                self.__push_to_aggregate(prv_pos, count)
                return True
    def generate(self, nparticles, real_time_display=True, display_progress=True):
        """Generates an aggregate consisting of `nparticles`.

        Arguments:
        ----------
        - nparticles -- Number of particles in the aggregate.
        - real_time_display -- Determines whether to plot the aggregate simulation
        in real time.

        Returns:
        --------
        A tuple consisting of a copy of the aggregate particle co-ordinates and a copy
        of the colors of each corresponding particle.
        """
        attrange = self.__initialise_attractor()
        self.__aggregate = np.zeros((nparticles, 2), dtype=int)
        # initialise colors for each particle in aggregate
        self.__colors = np.zeros(nparticles, dtype=(float, 3))
        clrpr.blue_through_red(self.__colors)
        aggrange = np.arange(nparticles)
        current = np.zeros(2, dtype=int)
        has_next_spawned = False
        count = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous = np.empty_like(current)
            previous[:] = current
            self.__update_brownian_particle(current)
            self.__lattice_boundary_collision(current, previous)
            if self.__aggregate_collision(current, previous, count, aggrange, attrange):
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
        if display_progress:
            pbar.finish()
        return self.__aggregate[:], self.__colors[:]
