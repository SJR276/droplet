from enum import Enum
import numpy as np
from numpy.random import rand

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
        self._stickiness = stickiness
        self.lattice_type = lattice_type
        if (attractor_type == AttractorType.SPHERE or
                attractor_type == AttractorType.PLANE):
            raise ValueError("Attractor type must be of a 2D topology for 2D aggregates")
        self._attractor_type = attractor_type
        self.aggregate = np.array()
        self.__spawn_diam = 8
        self.__max_radius_sqd = 0
    @property
    def stickiness(self):
        """Returns the stickiness property of the aggregate. This describes
        the probability of a particle sticking to the aggregate upon collision.

        Returns:
        --------
        The aggregate stickiness parameter.
        """
        return self._stickiness
    @stickiness.setter
    def stickiness(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self._stickiness = value
    @property
    def attractor_type(self):
        """Returns the type of the attractor used for the aggregate's initial seed.

        Returns:
        --------
        Type of attractor seed.
        """
        return self._attractor_type
    @attractor_type.setter
    def attractor_type(self, value):
        if (value == AttractorType.SPHERE or
                value == AttractorType.PLANE):
            raise ValueError("Attractor type must be of a 2D topology for 2D aggregates")
        self._attractor_type = value
    def __spawn_brownian_particle(self, crr_pos):
        ppr = rand()
        if self._attractor_type == AttractorType.POINT:
            if ppr < 0.5:
                crr_pos[0] = (int)(self.__spawn_diam*(rand() - 0.5))
                if ppr < 0.25:
                    crr_pos[1] = (int)(self.__spawn_diam*0.5)
                else:
                    crr_pos[1] = -(int)(self.__spawn_diam*0.5)
            else:
                if ppr < 0.75:
                    crr_pos[0] = (int)(self.__spawn_diam*0.5)
                else:
                    crr_pos[0] = -(int)(self.__spawn_diam*0.5)
                crr_pos[1] = (int)(self.__spawn_diam*(rand() - 0.5))
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
    def __lattice_boundary_collision(self, crr_pos, prv_pos):
        epsilon = 2
        if self._attractor_type == AttractorType.POINT:
            if (np.abs(crr_pos[0]) > (self.__spawn_diam/2 + epsilon) or
                    np.abs(crr_pos[1]) > (self.__spawn_diam/2 + epsilon)):
                crr_pos = prv_pos
    def __aggregate_collision(self, crr_pos, prv_pos):
        if rand() > self._stickiness:
            return False
        for p in np.nditer(self.aggregate):
            if p == crr_pos:
                self.aggregate[-1] = prv_pos
                radius_sqd = prv_pos[0]**2 + prv_pos[1]**2
                if radius_sqd > self.__max_radius_sqd:
                    self.__max_radius_sqd = radius_sqd
                    self.__spawn_diam = radius_sqd + 8
                return True
    def generate(self, nparticles, real_time_display=True):
        """Generates an aggregate consisting of `nparticles`.

        Arguments:
        ----------
        - nparticles -- Number of particles in the aggregate.
        - real_time_display -- Determines whether to plot the aggrgete simulation
        in real time.
        """
        self.aggregate = np.zeros(nparticles)
        # current co-ordinates
        current = np.zeros(2)
        has_next_spawned = False
        count = 0
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous = current
            self.__update_brownian_particle(current)
            self.__lattice_boundary_collision(current, previous)
            if self.__aggregate_collision(current, previous):
                count += 1
                has_next_spawned = False
            