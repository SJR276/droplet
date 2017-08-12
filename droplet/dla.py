import os.path
from ctypes import CDLL, Structure, POINTER, byref, cast
from ctypes import c_size_t, c_ubyte, c_double, c_int
from enum import Enum
import numpy as np
from numpy.random import rand
import droplet.colorprofiles as clrpr
import droplet.external.progressbar as pb

LIBDROPLETNAME = "libdroplet.so"
LIBDROPLETPATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LIBDROPLETNAME
LIBDRP = CDLL(LIBDROPLETPATH)

class _VectorWrapper(Structure):
    _fields_ = [
        ("data", POINTER(c_ubyte)),
        ("size", c_size_t),
        ("elemsize", c_size_t),
        ("capacity", c_size_t)]

class _AggregateWrapper(Structure):
    _fields_ = [
        ("_aggregate", POINTER(_VectorWrapper)),
        ("_attractor", POINTER(_VectorWrapper)),
        ("_bcolls", POINTER(_VectorWrapper)),
        ("_rsteps", POINTER(_VectorWrapper)),
        ("stickiness", c_double),
        ("max_x", c_size_t),
        ("max_y", c_size_t),
        ("max_r_sqd", c_size_t),
        ("b_offset", c_size_t),
        ("spawn_diam", c_size_t),
        ("att_size", c_size_t),
        ("lt", c_int),
        ("at", c_int)]

class _Pair(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int)]

class LatticeType(Enum):
    """The geometry of a lattice."""
    SQUARE = 1
    TRIANGLE = 2

class AttractorType(Enum):
    """The initial attractor seed of an aggregate."""
    POINT = 1
    CIRCLE = 2
    SPHERE = 3
    LINE = 4
    PLANE = 5

class Aggregate2D(object):
    """A two-dimensional DLA structure."""
    def __init__(self, stickiness=1.0):
        self._this = _AggregateWrapper()
        self._handle = byref(self._this)
        retval = LIBDRP.aggregate_2d_init(self._handle, c_double(stickiness))
        if retval == -1:
            raise MemoryError("vector allocation failure occurred in aggregate_2d_init.")
    def __del__(self):
        LIBDRP.aggregate_2d_free_fields(self._handle)
    def generate(self, nparticles):
        """Generates an aggregate consisting of `nparticles`.

        Parameters
        ----------
        nparticles -- Size of aggregate to generate.
        """
        retval = LIBDRP.aggregate_2d_generate(self._handle, c_size_t(nparticles))
        if retval == -1:
            raise MemoryError("vector reallocation failured occurred in aggregate_2d_generate.")

def agg2d_as_ndarray(agg2d):
    """Copies the internal (C) aggregate structure of an `Aggregate2D`
    object to a `np.ndarray` with `shape=(n, 2)` where n is the size
    of the aggregate.

    Parameters
    ----------
    agg2d -- Object of type `Aggregate2D`.

    Returns:
    --------
    `np.ndarray` containing aggregate particle co-ordinates.
    """
    assert isinstance(agg2d, Aggregate2D)
    aggsize = LIBDRP.vector_size(agg2d._this._aggregate)
    ret = np.zeros((aggsize, 2), dtype=int)
    for idx in np.arange(aggsize):
        addr = LIBDRP.vector_at(agg2d._this._aggregate, c_size_t(idx))
        aggp = cast(addr, POINTER(_Pair)).contents
        ret[idx][0] = aggp.x
        ret[idx][1] = aggp.y
    return ret

class DiffusionLimitedAggregate2D(object):
    """A two-dimensional Diffusion Limited Aggregate (DLA) structure
    with associated properties such as the aggregate stickiness, the
    type of lattice and the type of attractor used.
    """
    def __init__(self, stickiness=1.0, lattice_type=LatticeType.SQUARE,
                 attractor_type=AttractorType.POINT,
                 color_profile=clrpr.ColorProfile.BLUETHROUGHRED):
        """Create a `DiffusionLimitedAggregate2D` instance with specified
        properties.

        Parameters:
        -----------
        - stickiness -- Floating point value in [0, 1] determining probability
        of a particle sticking to the aggregate upon collision.
        - lattice_type -- Type of lattice upon which to execute aggregate generation.
        - attractor_type -- Type of initial attractor seed.
        - color_profile -- Color gradient of aggregate particles.

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
        self.__reqd_steps = np.array(0)
        self.__boundary_colls = np.array(0)
        self.attractor_size = 1
        self.color_profile = color_profile
        self.__boundary_offset = 6
        self.__spawn_diam = self.__boundary_offset
        self.__max_radius_sqd = 0
        self.__max_x = 0
        self.__max_y = 0
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
        """Sets the value of the stickiness of the aggregate. This parameter determines
        the probability of a particle sticking to the aggregate upon collision.

        Parameters:
        -----------
        value -- Value of the stickiness to set.

        Exceptions:
        -----------
        Raises `ValueError` if `value` not in [0, 1].
        """
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
        """Sets the value of the attractor type of the aggregate.

        Parameters:
        -----------
        value -- Type of attractor seed to set.

        Exceptions:
        -----------
        Raises `ValueError` if `value` corresponds to a 3D geometry attractor seed.
        """
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
        return (self.__aggregate[:, 0])[:]
    @property
    def y_coords(self):
        """Returns the y co-ordinates of all particles in the aggregate. This
        is a readonly property, useful for plotting.

        Returns:
        --------
        The y co-ordinates of the aggregate particles.
        """
        return (self.__aggregate[:, 1])[:]
    @property
    def colors(self):
        """Returns the color array of all particles (un order) in the aggregate.
        This ia a readonly property, useful for plotting.
        """
        return self.__colors[:]
    @property
    def required_steps(self):
        """Returns the number of lattice steps required for each particle to stick
        to the aggregate.

        Returns:
        --------
        The number of steps on the lattice each particle was required to complete
        before sticking to the aggregate.
        """
        return self.__reqd_steps[:]
    @property
    def boundary_collisions(self):
        """Returns the number of boundary collisions each random-walking particle
        experienced before sticking to the aggregate.

        Returns:
        --------
        Number of boundary collisions experienced by each particle.
        """
        return self.__boundary_colls[:]
    def __initialise_attractor(self):
        if self.__attractor_type == AttractorType.POINT:
            self.__attractor = np.zeros((1, 2))
            return np.arange(1)
        elif self.__attractor_type == AttractorType.LINE:
            self.__attractor = np.zeros((self.attractor_size, 2), dtype=int)
            self.__attractor[:, 0] = (np.arange(self.attractor_size)
                                      - (int)(0.5*self.attractor_size))
            return np.arange(self.attractor_size)
        elif self.__attractor_type == AttractorType.CIRCLE:
            self.__attractor = np.zeros(((int)(2.0*np.pi*self.attractor_size)+1, 2), dtype=int)
            #angles = np.arange(0.0, 2.0*np.pi, step=np.pi/100)
            angles = np.arange(0.0, 2.0*np.pi, step=1.0/self.attractor_size)
            count = 0
            for theta in angles:
                self.__attractor[count][0] = self.attractor_size*np.cos(theta)
                self.__attractor[count][1] = self.attractor_size*np.sin(theta)
                count += 1
            return np.arange(len(angles))
    def __push_attractor_to_aggregate(self, attrange):
        for idx in attrange:
            pos_x = self.__attractor[idx][0]
            pos_y = self.__attractor[idx][1]
            self.__aggregate[idx][0] = pos_x
            self.__aggregate[idx][1] = pos_y
            if self.__attractor_type == AttractorType.POINT:
                radius_sqd = pos_x*pos_x + pos_y*pos_y
                if radius_sqd > self.__max_radius_sqd:
                    self.__max_radius_sqd = radius_sqd
                    self.__spawn_diam = 2*(int)(radius_sqd**0.5) + self.__boundary_offset
            elif self.__attractor_type == AttractorType.LINE:
                if pos_y > self.__max_y:
                    self.__max_y = pos_y
                    self.__spawn_diam = pos_y + self.__boundary_offset
        if self.__attractor_type == AttractorType.CIRCLE:
            self.__spawn_diam = self.attractor_size + self.__boundary_offset
    def __spawn_brownian_particle(self, crr_pos):
        ppr = rand()
        if self.__attractor_type == AttractorType.POINT:
            if ppr < 0.5:
                crr_pos[0] = self.__spawn_diam*(rand() - 0.5)
                crr_pos[1] = (self.__spawn_diam*0.5 if ppr < 0.25 else
                              -self.__spawn_diam*0.5)
            else:
                crr_pos[0] = (self.__spawn_diam*0.5 if ppr < 0.75 else
                              -self.__spawn_diam*0.5)
                crr_pos[1] = self.__spawn_diam*(rand() - 0.5)
        elif self.__attractor_type == AttractorType.LINE:
            crr_pos[0] = 2*self.attractor_size*(rand() - 0.5)
            crr_pos[1] = (self.__spawn_diam if ppr < 0.5 else -self.__spawn_diam)
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
        epsilon = 2 # small correction for slightly elastic boundaries
        if (self.__attractor_type == AttractorType.POINT or
                self.__attractor_type == AttractorType.CIRCLE):
            boundary_absmax = (int)(self.__spawn_diam*0.5 + epsilon)
            if (np.abs(crr_pos[0]) > boundary_absmax or
                    np.abs(crr_pos[1]) > boundary_absmax):
                crr_pos[:] = prv_pos
                return True
        elif self.__attractor_type == AttractorType.LINE:
            if (np.abs(crr_pos[0]) > 2*self.attractor_size or
                    np.abs(crr_pos[1]) > self.__spawn_diam + epsilon):
                crr_pos[:] = prv_pos
                return True
        return False
    def __push_to_aggregate(self, particle, count):
        self.__aggregate[count+self.attractor_size][0] = particle[0]
        self.__aggregate[count+self.attractor_size][1] = particle[1]
        # check if we need to expand the spawning region
        if self.__attractor_type == AttractorType.POINT:
            radius_sqd = particle[0]*particle[0] + particle[1]*particle[1]
            if radius_sqd > self.__max_radius_sqd:
                self.__max_radius_sqd = radius_sqd
                self.__spawn_diam = 2*(int)(radius_sqd**0.5) + self.__boundary_offset
        elif self.__attractor_type == AttractorType.LINE:
            if particle[1] > self.__max_y:
                self.__max_y = particle[1]
                self.__spawn_diam = particle[1] + self.__boundary_offset
        elif self.__attractor_type == AttractorType.CIRCLE:
            radius_sqd = (particle[0]*particle[0] + particle[1]*particle[1] +
                          self.attractor_size*self.attractor_size)
            if radius_sqd > self.__max_radius_sqd:
                self.__max_radius_sqd = radius_sqd
                self.__spawn_diam = 2*(int)(radius_sqd**0.5) + self.__boundary_offset
    def __aggregate_collision(self, crr_pos, prv_pos, count, agg_range):
        """Checks for collision of a particle undergoing Brownian motion with
        the aggregate or attractor structure, and adds the particle to the
        aggregate if a collision does occur.

        Parameters:
        -----------
        crr_pos -- Current position of particle.
        prv_pos -- Previous position of particle.
        count -- Number of particles stuck to the aggregate.
        agg_range -- A `np.arange` array with a size corresponding to number of
        particles to generate.

        Returns:
        --------
        `True` if a collision occurred, `False` otherwise.
        """
        if rand() > self.__stickiness:
            return False
        # check for collision with aggregate structure
        for idx in agg_range:
            if (self.__aggregate[idx][0] == crr_pos[0] and
                    self.__aggregate[idx][1] == crr_pos[1]):
                self.__push_to_aggregate(prv_pos, count)
                return True
    def generate_stream(self, nparticles, display_progress=True):
        """Generator function for streaming aggregate data to a real-time plot.

        Parameters:
        -----------
        - nparticles -- Number of particles, i.e. size of aggregate, to generate.
        - display_progress -- Determines whether to print a progress bar to `stdout`
        showing progress to completion.
        """
        attrange = self.__initialise_attractor()
        self.__aggregate = np.zeros((nparticles+self.attractor_size, 2), dtype=int)
        self.__push_attractor_to_aggregate(attrange)
        self.__reqd_steps = np.zeros(nparticles, dtype=int)
        self.__boundary_colls = np.zeros(nparticles, dtype=int)
        # initialise colors for each particle in aggregate
        self.__colors = np.zeros(2*(nparticles+self.attractor_size), dtype=(float, 3))
        clrpr.blue_through_red(self.__colors)
        aggrange = np.arange(nparticles)
        current = np.zeros(2, dtype=int)
        previous = np.zeros(2, dtype=int)
        has_next_spawned = False
        count = 0
        steps_to_stick = 0
        bcolls = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous[:] = current
            self.__update_brownian_particle(current)
            if self.__lattice_boundary_collision(current, previous):
                bcolls += 1
            steps_to_stick += 1
            if self.__aggregate_collision(current, previous, count, aggrange):
                self.__reqd_steps[count] = steps_to_stick
                self.__boundary_colls[count] = bcolls
                steps_to_stick = 0
                bcolls = 0
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
                yield self.__aggregate, self.__colors, count
        if display_progress:
            pbar.finish()
    def generate(self, nparticles, display_progress=True):
        """Generates an aggregate consisting of `nparticles`.

        Parameters:
        -----------
        - nparticles -- Number of particles, i.e. size of aggregate, to generate.
        - display_progress -- Determines whether to print a progress bar to `stdout`
        showing progress to completion.

        Returns:
        --------
        A tuple consisting of a copy of the aggregate particle co-ordinates and a copy
        of the colors of each corresponding particle.
        """
        attrange = self.__initialise_attractor()
        self.__aggregate = np.zeros((nparticles+len(attrange), 2), dtype=int)
        self.__push_attractor_to_aggregate(attrange)
        self.__reqd_steps = np.zeros(nparticles, dtype=int)
        self.__boundary_colls = np.zeros(nparticles, dtype=int)
        # initialise colors for each particle in aggregate
        self.__colors = np.zeros(nparticles+len(attrange), dtype=(float, 3))
        clrpr.blue_through_red(self.__colors)
        aggrange = np.arange(nparticles)
        current = np.zeros(2, dtype=int)
        previous = np.zeros(2, dtype=int)
        has_next_spawned = False
        count = 0
        steps_to_stick = 0
        bcolls = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous[:] = current
            self.__update_brownian_particle(current)
            if self.__lattice_boundary_collision(current, previous):
                bcolls += 1
            steps_to_stick += 1
            if self.__aggregate_collision(current, previous, count, aggrange):
                self.__reqd_steps[count] = steps_to_stick
                self.__boundary_colls[count] = bcolls
                steps_to_stick = 0
                bcolls = 0
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
        if display_progress:
            pbar.finish()
        return self.__aggregate[:], self.__colors[:]

class DiffusionLimitedAggregate3D(object):
    """A three-dimensional Diffusion Limited Aggregate (DLA) structure
    with associated properties such as the aggregate stickiness, the
    type of lattice and the type of attractor used.
    """
    def __init__(self, stickiness=1.0, lattice_type=LatticeType.SQUARE,
                 attractor_type=AttractorType.POINT,
                 color_profile=clrpr.ColorProfile.BLUETHROUGHRED):
        if stickiness < 0.0 or stickiness > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self.__stickiness = stickiness
        self.lattice_type = lattice_type
        self.attractor_type = attractor_type
        self.__aggregate = np.array(0)
        self.__colors = np.array(0)
        self.__attractor = np.array(0)
        self.__reqd_steps = np.array(0)
        self.__boundary_colls = np.array(0)
        self.attractor_size = 1
        self.color_profile = color_profile
        self.__boundary_offset = 6
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
        """Sets the value of the stickiness of the aggregate. This parameter determines
        the probability of a particle sticking to the aggregate upon collision.

        Parameters:
        -----------
        value -- Value of the stickiness to set.

        Exceptions:
        -----------
        Raises `ValueError` if `value` not in [0, 1].
        """
        if value < 0.0 or value > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self.__stickiness = value
    @property
    def x_coords(self):
        """Returns the x co-ordinates of all particles in the aggregate. This
        is a readonly property, useful for plotting.

        Returns:
        --------
        The x co-ordinates of the aggregate particles.
        """
        return (self.__aggregate[:, 0])[:]
    @property
    def y_coords(self):
        """Returns the y co-ordinates of all particles in the aggregate. This
        is a readonly property useful for plotting.

        Returns:
        --------
        The y co-ordinates of the aggregate particles.
        """
        return (self.__aggregate[:, 1])[:]
    @property
    def z_coords(self):
        """Returns the z co-ordinates of all particles in the aggregate. This
        is a readonly property useful for plotting.

        Returns:
        --------
        The z co-ordinates of the aggregate particles.
        """
        return (self.__aggregate[:, 2])[:]
    @property
    def colors(self):
        """Returns the color array of all particles in the aggregate. This is
        a readonly property, useful for plotting.
        """
        return self.__colors[:]
    @property
    def required_steps(self):
        """Returns the number of lattice steps required for each particle to stick
        to the aggregate.

        Returns:
        --------
        The number of steps on the lattice each particle was required to complete
        before sticking to the aggregate.
        """
        return self.__reqd_steps[:]
    @property
    def boundary_collisions(self):
        """Returns the number of boundary collisions each random-walking particle
        experienced before sticking to the aggregate.

        Returns:
        --------
        Number of boundary collisions experienced by each particle.
        """
        return self.__boundary_colls[:]
    def __initialise_attractor(self):
        if self.attractor_type == AttractorType.POINT:
            self.__attractor = np.zeros((1, 3))
            return np.arange(1)
        elif self.attractor_type == AttractorType.LINE:
            self.__attractor = np.zeros((self.attractor_size, 3), dtype=int)
            self.__attractor[:, 0] = (np.arange(self.attractor_size)
                                      - (int)(0.5*self.attractor_size))
            return np.arange(self.attractor_size)
    def __push_attractor_to_aggregate(self, attrange):
        for idx in attrange:
            self.__aggregate[idx][0] = self.__attractor[idx][0]
            self.__aggregate[idx][1] = self.__attractor[idx][1]
            self.__aggregate[idx][2] = self.__attractor[idx][2]
    def __spawn_brownian_particle(self, crr_pos):
        ppr = rand()
        if self.attractor_type == AttractorType.POINT:
            if ppr < 1.0/3.0:
                crr_pos[0] = self.__spawn_diam*(rand() - 0.5)
                crr_pos[1] = self.__spawn_diam*(rand() - 0.5)
                crr_pos[2] = (0.5*self.__spawn_diam if ppr < 1.0/6.0 else
                              -0.5*self.__spawn_diam)
            elif ppr >= 1.0/3.0 and ppr < 2.0/3.0:
                crr_pos[0] = (0.5*self.__spawn_diam if ppr < 0.5 else
                              -0.5*self.__spawn_diam)
                crr_pos[1] = self.__spawn_diam*(rand() - 0.5)
                crr_pos[2] = self.__spawn_diam*(rand() - 0.5)
            else:
                crr_pos[0] = self.__spawn_diam*(rand() - 0.5)
                crr_pos[1] = (0.5*self.__spawn_diam if ppr < 5.0/6.0 else
                              -0.5*self.__spawn_diam)
                crr_pos[2] = self.__spawn_diam*(rand() - 0.5)
    def __update_brownian_particle(self, crr_pos):
        mov_dir = rand()
        if self.lattice_type == LatticeType.SQUARE:
            if mov_dir < 1.0/6.0:
                crr_pos[0] += 1
            elif mov_dir >= 1.0/6.0 and mov_dir < 2.0/6.0:
                crr_pos[0] -= 1
            elif mov_dir >= 2.0/6.0 and mov_dir < 0.5:
                crr_pos[1] += 1
            elif mov_dir >= 0.5 and mov_dir < 4.0/6.0:
                crr_pos[1] -= 1
            elif mov_dir >= 4.0/6.0 and mov_dir < 5.0/6.0:
                crr_pos[2] += 1
            else:
                crr_pos[2] -= 1
        elif self.lattice_type == LatticeType.TRIANGLE:
            if mov_dir < 1.0/8.0:
                crr_pos[0] += 1
                crr_pos[1] += 1
            elif mov_dir >= 1.0/8.0 and mov_dir < 0.25:
                crr_pos[0] += 1
                crr_pos[1] -= 1
            elif mov_dir >= 0.25 and mov_dir < 3.0/8.0:
                crr_pos[0] -= 1
                crr_pos[1] -= 1
            elif mov_dir >= 3.0/8.0 and mov_dir < 0.5:
                crr_pos[0] -= 1
                crr_pos[1] += 1
            elif mov_dir >= 0.5 and mov_dir < 5.0/8.0:
                crr_pos[0] += 1
            elif mov_dir >= 5.0/8.0 and mov_dir < 0.75:
                crr_pos[0] -= 1
            elif mov_dir >= 0.75 and mov_dir < 7.0/8.0:
                crr_pos[2] += 1
            else:
                crr_pos[2] -= 1
    def __lattice_boundary_collision(self, crr_pos, prv_pos):
        epsilon = 2
        boundary_absmax = (int)(self.__spawn_diam*0.5 + epsilon)
        if self.attractor_type == AttractorType.POINT:
            if (np.abs(crr_pos[0]) > boundary_absmax or
                    np.abs(crr_pos[1]) > boundary_absmax or
                    np.abs(crr_pos[2]) > boundary_absmax):
                crr_pos[:] = prv_pos
                return True
        return False
    def __push_to_aggregate(self, particle, count):
        self.__aggregate[count + self.attractor_size][0] = particle[0]
        self.__aggregate[count + self.attractor_size][1] = particle[1]
        self.__aggregate[count + self.attractor_size][2] = particle[2]
        radius_sqd = (particle[0]*particle[0] + particle[1]*particle[1]
                      + particle[2]*particle[2])
        if radius_sqd > self.__max_radius_sqd:
            self.__max_radius_sqd = radius_sqd
            self.__spawn_diam = 2*(int)(radius_sqd**0.5) + self.__boundary_offset
    def __aggregate_collision(self, crr_pos, prv_pos, count, agg_range):
        if rand() > self.__stickiness:
            return False
        for idx in agg_range:
            if (self.__aggregate[idx][0] == crr_pos[0] and
                    self.__aggregate[idx][1] == crr_pos[1] and
                    self.__aggregate[idx][2] == crr_pos[2]):
                self.__push_to_aggregate(prv_pos, count)
                return True
    def generate_stream(self, nparticles, display_progress=True):
        """Generator function for streaming aggregate data to a real-time plot.

        Parameters:
        -----------
        nparticles -- Number of particles, i.e. size of aggregate, to generate.
        display_progress -- Determines whether to print a progress bar to stdout
        showing progress to completion.
        """
        attrange = self.__initialise_attractor()
        self.__aggregate = np.zeros((nparticles + self.attractor_size, 3), dtype=int)
        self.__push_attractor_to_aggregate(attrange)
        self.__reqd_steps = np.zeros(nparticles, dtype=int)
        self.__boundary_colls = np.zeros(nparticles, dtype=int)
        self.__colors = np.zeros(2*(nparticles+self.attractor_size), dtype=(float, 3))
        clrpr.blue_through_red(self.__colors)
        aggrange = np.arange(nparticles)
        current = np.zeros(3, dtype=int)
        previous = np.zeros(3, dtype=int)
        has_next_spawned = False
        count = 0
        steps_to_stick = 0
        bcolls = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous[:] = current
            self.__update_brownian_particle(current)
            if self.__lattice_boundary_collision(current, previous):
                bcolls += 1
            steps_to_stick += 1
            if self.__aggregate_collision(current, previous, count, aggrange):
                self.__reqd_steps[count] = steps_to_stick
                self.__boundary_colls[count] = bcolls
                steps_to_stick = 0
                bcolls = 0
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
                yield self.__aggregate, self.__colors, count
        if display_progress:
            pbar.finish()
    def generate(self, nparticles, display_progress=True):
        """Generates an aggregate consisting of `nparticles`.

        Parameters:
        -----------
        nparticles -- Number of particles, i.e. size of aggregate, to generate.
        display_progress -- Determines whether to print a progress bar to stdout
        showing progress to completion.

        Returns:
        --------
        A tuple consisting of a copy of the aggregate particle co-ordinates and a copy
        of the colors of each corresponding particle.
        """
        attrange = self.__initialise_attractor()
        self.__aggregate = np.zeros((nparticles + self.attractor_size, 3), dtype=int)
        self.__push_attractor_to_aggregate(attrange)
        self.__reqd_steps = np.zeros(nparticles, dtype=int)
        self.__boundary_colls = np.zeros(nparticles, dtype=int)
        self.__colors = np.zeros(nparticles+self.attractor_size, dtype=(float, 3))
        clrpr.blue_through_red(self.__colors)
        aggrange = np.arange(nparticles)
        current = np.zeros(3, dtype=int)
        previous = np.zeros(3, dtype=int)
        has_next_spawned = False
        count = 0
        steps_to_stick = 0
        bcolls = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                self.__spawn_brownian_particle(current)
                has_next_spawned = True
            previous[:] = current
            self.__update_brownian_particle(current)
            if self.__lattice_boundary_collision(current, previous):
                bcolls += 1
            steps_to_stick += 1
            if self.__aggregate_collision(current, previous, count, aggrange):
                self.__reqd_steps[count] = steps_to_stick
                self.__boundary_colls[count] = bcolls
                steps_to_stick = 0
                bcolls = 0
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
        if display_progress:
            pbar.finish()
        return self.__aggregate[:], self.__colors[:]
