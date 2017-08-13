import os.path
from ctypes import CDLL, Structure, POINTER, byref, cast, sizeof
from ctypes import c_size_t, c_ubyte, c_double, c_int, c_bool
from enum import Enum
import numpy as np
from numpy.random import rand
import droplet.colorprofiles as clrpr
import droplet.external.progressbar as pb

LIBDROPLETNAME = "libdroplet.so"
LIBDROPLETPATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LIBDROPLETNAME
LIBDRP = CDLL(LIBDROPLETPATH)

_C_SIZE_T_PTR_T = POINTER(c_size_t)

class _IntPair(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int)]

class _IntTriplet(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("z", c_int)]

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
        ("max_z", c_size_t),
        ("max_r_sqd", c_size_t),
        ("b_offset", c_size_t),
        ("spawn_diam", c_size_t),
        ("att_size", c_size_t),
        ("lt", c_int),
        ("at", c_int)]

class LatticeType(Enum):
    """The geometry of a lattice."""
    SQUARE = 0
    TRIANGLE = 1

class AttractorType(Enum):
    """The initial attractor seed of an aggregate."""
    POINT = 0
    CIRCLE = 1
    SPHERE = 2
    LINE = 3
    PLANE = 4

class Aggregate2D(object):
    """A two-dimensional Diffusion Limited Aggregate."""
    def __init__(self, stickiness=1.0, lattice_type=LatticeType.SQUARE,
                 attractor_type=AttractorType.POINT,
                 color_profile=clrpr.ColorProfile.BLUETHROUGHRED):
        """Initialises the aggregate with the specified properties.

        Parameters
        ----------
        *stickiness* :: `float`, optional, default = 1.0

            Probability of a particle sticking to the aggregate.

        *lattice_type* :: `droplet.LatticeType`, optional, default = `SQUARE`

            Type of lattice to generate aggregate upon.

        *attractor_type* :: `droplet.AttractorType`, optional, default = `POINT`

            Type of initial attractor geometry.

        *color_profile* :: `droplet.colorprofiles.ColorProfile`, optional,
        default = `BLUETHROUGHRED`

            Color profile of aggregate structure.

        Exceptions
        ----------
        Raises `MemoryError` if a vector allocation failure occurs.
        """
        self._this = _AggregateWrapper()
        self._handle = byref(self._this)
        retval = LIBDRP.aggregate_2d_init(self._handle, c_double(stickiness),
                                          c_int(lattice_type.value),
                                          c_int(attractor_type.value))
        if retval == -1:
            raise MemoryError("vector allocation failure occurred in aggregate_2d_init.")
        self.color_profile = color_profile
        self.colors = np.array(0)
        self.__aggregate = np.array(0)
    def __del__(self):
        LIBDRP.aggregate_free_fields(self._handle)
    @property
    def stickiness(self):
        """Returns the stickiness property of the aggregate. This describes
        the probability of a particle sticking to the aggregate upon collision.

        Returns
        -------
        The aggregate stickiness parameter.
        """
        return self._this.stickiness
    @stickiness.setter
    def stickiness(self, value):
        """Sets the value of the stickiness of the aggregate. This parameter determines
        the probability of a particle sticking to the aggregate upon collision.

        Parameters
        ----------
        *value* :: `float`

            Value of the stickiness to set.

        Exceptions
        ----------
        Raises `ValueError` if `value` not in [0, 1].
        """
        if value < 0.0 or value > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self._this.stickiness = c_double(value)
    @property
    def attractor_size(self):
        """Returns the size of the attractor seed, the physical interpretation of
        this value depends upon the attractor geometry type set.

        Returns
        -------
        Size of the attractor.
        """
        return self._this.att_size
    @attractor_size.setter
    def attractor_size(self, value):
        """Sets the size of the attractor seed.

        Parameters
        ----------
        *value* :: `int`

            Size of attractor to set.
        """
        self._this.att_size = c_size_t(value)
    @property
    def required_steps(self):
        """Returns the number of lattice steps required for each particle to stick
        to the aggregate.

        Returns
        -------
        The number of steps on the lattice each particle was required to complete
        before sticking to the aggregate.
        """
        aggsize = LIBDRP.vector_size(self._this._rsteps)
        ret = np.zeros(aggsize, dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._rsteps, c_size_t(idx))
            ret[idx] = cast(addr, _C_SIZE_T_PTR_T).contents.value
        return ret
    @property
    def boundary_collisions(self):
        """Returns the number of boundary collisions each random-walking particle
        experienced before sticking to the aggregate.

        Returns
        -------
        Number of boundary collisions experienced by each particle.
        """
        aggsize = LIBDRP.vector_size(self._this._bcolls)
        ret = np.zeros(aggsize, dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._bcolls, c_size_t(idx))
            ret[idx] = cast(addr, _C_SIZE_T_PTR_T).contents.value
        return ret
    @property
    def max_x(self):
        """Obtains the maximum x co-ordinate value of the aggregate.

        Returns
        -------
        Maximum extent of the aggregate in the x-direction.
        """
        return self._this.max_x
    @property
    def max_y(self):
        """Obtains the maximum y co-ordinate value of the aggregate.

        Returns
        -------
        Maximum extent of the aggregate in the y-direction.
        """
        return self._this.max_y
    @property
    def radius(self):
        """Returns the radius of the smallest circle which bounds all
        particles in the aggregate.

        Returns
        -------
        Value of the radius of smallest bounding circle.
        """
        return np.sqrt(self._this.max_r_sqd)
    @property
    def size(self):
        """Returns the size of the aggregate in terms of the total number
        of particles - including the initial attractor seed.

        Returns
        -------
        Size of the aggregate.
        """
        return LIBDRP.vector_size(self._this._aggregate)
    def fractal_dimension(self):
        """Computes the fractal dimension of the aggregate.

        Returns
        -------
        Dimension of the aggregate fractal.
        """
        return np.log(self.size)/np.log(self.radius)
    def as_ndarray(self):
        """Copies the internal (C) aggregate structure to a `np.ndarray`
        with `shape=(n, 2)` where `n` is the size of the aggregate.

        Returns
        -------
        An instance of `np.ndarray` containing aggregate particle co-ordinates.
        """
        _IntPair_ptr_t = POINTER(_IntPair)
        aggsize = LIBDRP.vector_size(self._this._aggregate)
        ret = np.zeros((aggsize, 2), dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._aggregate, c_size_t(idx))
            aggp = cast(addr, _IntPair_ptr_t).contents
            ret[idx][0] = aggp.x
            ret[idx][1] = aggp.y
        return ret
    def generate(self, nparticles, display_progress=True):
        """Generates an aggregate consisting of `nparticles`.

        Parameters
        ----------
        *nparticles* :: `int`

            Size of aggregate to generate.

        *display_progress* :: `bool`, optional, default = True

            Print progress bar to terminal.

        Exceptions
        ----------
        Raises `MemoryError` if a vector reallocation failure occurs.
        """
        retval = LIBDRP.aggregate_2d_generate(self._handle,
                                              c_size_t(nparticles),
                                              c_bool(display_progress))
        if retval == -1:
            raise MemoryError("vector reallocation failure occurred in aggregate_2d_generate.")
        # initialise colors for each particle in aggregate
        self.colors = np.zeros(nparticles+self._this.att_size, dtype=(float, 3))
        clrpr.blue_through_red(self.colors)
    def generate_stream(self, nparticles, display_progress=False):
        """Generator function for streaming aggregate data to a real-time plot.

        Parameters
        ----------
        *nparticles* :: `int`

            Size of aggregate to generate.

        *display_progress* :: `bool`, optional, default = False

            Print progress bar to terminal.

        Exceptions
        ----------
        Raises `MemoryError` if a vector reallocation failure occurs.
        """
        LIBDRP.aggregate_2d_lattice_collision.restype = c_bool
        LIBDRP.aggregate_2d_collision.restype = c_bool
        _IntPair_ptr_t = POINTER(_IntPair)
        rv_res = LIBDRP.aggregate_reserve(self._handle, c_size_t(nparticles))
        if rv_res == -1:
            raise MemoryError("vector reallocation failure occurred in aggregate_2d_reserve.")
        rv_ia = LIBDRP.aggregate_2d_init_attractor(self._handle, c_size_t(nparticles))
        if rv_ia == -1:
            raise MemoryError("""vector reallocation failure occurred in
            aggregate_2d_init_attractor.""")
        self.__aggregate = np.zeros((nparticles + self._this.att_size, 2), dtype=int)
        # initialise colors for each particle in aggregate
        self.colors = np.zeros(2*(nparticles+self._this.att_size), dtype=(float, 3))
        clrpr.blue_through_red(self.colors)
        curr = _IntPair()
        prev = _IntPair()
        has_next_spawned = False
        rsteps = c_size_t(0) # required steps to stick
        bcolls = c_size_t(0) # lattice boundary collisions before stick
        count = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                LIBDRP.aggregate_2d_spawn_bp(self._handle, byref(curr))
                has_next_spawned = True
            prev.x = curr.x
            prev.y = curr.y
            LIBDRP.aggregate_2d_update_bp(self._handle, byref(curr))
            if LIBDRP.aggregate_2d_lattice_collision(self._handle, byref(curr), byref(prev)):
                bcolls = c_size_t(bcolls.value + 1)
            rsteps = c_size_t(rsteps.value + 1)
            if LIBDRP.aggregate_2d_collision(self._handle, byref(curr), byref(prev)):
                addr_rec = LIBDRP.vector_at(self._this._aggregate,
                                            c_size_t(count + self._this.att_size))
                aggp_rec = cast(addr_rec, _IntPair_ptr_t).contents
                self.__aggregate[count+self._this.att_size][0] = aggp_rec.x
                self.__aggregate[count+self._this.att_size][1] = aggp_rec.y
                LIBDRP.vector_push_back(self._this._rsteps, byref(rsteps), sizeof(c_size_t))
                LIBDRP.vector_push_back(self._this._bcolls, byref(bcolls), sizeof(c_size_t))
                rsteps = c_size_t(0)
                bcolls = c_size_t(0)
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
                yield self.__aggregate, self.colors, count
        if display_progress:
            pbar.finish()

class Aggregate3D(object):
    """A three-dimensional Diffusion Limited Aggregate."""
    def __init__(self, stickiness=1.0, lattice_type=LatticeType.SQUARE,
                 attractor_type=AttractorType.POINT,
                 color_profile=clrpr.ColorProfile.BLUETHROUGHRED):
        """Initialises the aggregate with the specified properties.

        Parameters
        ----------
        *stickiness* :: `float`, optional, default = 1.0

            Probability of a particle sticking to the aggregate.

        *lattice_type* :: `droplet.LatticeType`, optional, default = `SQUARE`

            Type of lattice to generate aggregate upon.

        *attractor_type* :: `droplet.AttractorType`, optional, default = `POINT`

            Type of initial attractor geometry.

        *color_profile* :: `droplet.colorprofiles.ColorProfile`, optional,
        default = `BLUETHROUGHRED`

            Color profile of aggregate structure.

        Exceptions
        ----------
        Raises `MemoryError` if a vector allocation failure occurs.
        """
        self._this = _AggregateWrapper()
        self._handle = byref(self._this)
        retval = LIBDRP.aggregate_3d_init(self._handle, c_double(stickiness),
                                          c_int(lattice_type.value),
                                          c_int(attractor_type.value))
        if retval == -1:
            raise MemoryError("vector allocation failure occurred in aggregate_3d_init.")
        self.color_profile = color_profile
        self.colors = np.array(0)
        self.__aggregate = np.array(0)
    def __del__(self):
        LIBDRP.aggregate_free_fields(self._handle)
    @property
    def stickiness(self):
        """Returns the stickiness property of the aggregate. This describes
        the probability of a particle sticking to the aggregate upon collision.

        Returns
        -------
        The aggregate stickiness parameter.
        """
        return self._this.stickiness
    @stickiness.setter
    def stickiness(self, value):
        """Sets the value of the stickiness of the aggregate. This parameter determines
        the probability of a particle sticking to the aggregate upon collision.

        Parameters
        ----------
        *value* :: `float`

            Value of the stickiness to set.

        Exceptions
        ----------
        Raises `ValueError` if `value` not in [0, 1].
        """
        if value < 0.0 or value > 1.0:
            raise ValueError("Stickiness of aggregate must be in [0, 1].")
        self._this.stickiness = c_double(value)
    @property
    def attractor_size(self):
        """Returns the size of the attractor seed. The physical interpretation of
        this value depends upon the attractor geometry type set.

        Returns
        -------
        Size of the attractor.
        """
    @attractor_size.setter
    def attractor_size(self, value):
        """Sets the size of the attractor seed.

        Parameters
        ----------
        *value* :: `int`

            Size of attractor to set.
        """
        self._this.att_size = c_size_t(value)
    @property
    def required_steps(self):
        """Returns the number of lattice steps required for each particle to stick
        to the aggregate.

        Returns
        -------
        The number of steps on the lattice each particle was required to complete
        before sticking to the aggregate.
        """
        aggsize = LIBDRP.vector_size(self._this._rsteps)
        ret = np.zeros(aggsize, dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._rsteps, c_size_t(idx))
            ret[idx] = cast(addr, _C_SIZE_T_PTR_T).contents.value
        return ret
    @property
    def boundary_collisions(self):
        """Returns the number of boundary collisions each random-walking particle
        experienced before sticking to the aggregate.

        Returns
        -------
        Number of boundary collisions experienced by each particle.
        """
        aggsize = LIBDRP.vector_size(self._this._bcolls)
        ret = np.zeros(aggsize, dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._bcolls, c_size_t(idx))
            ret[idx] = cast(addr, _C_SIZE_T_PTR_T).contents.value
        return ret
    @property
    def max_x(self):
        """Obtains the maximum x co-ordinate value of the aggregate.

        Returns
        -------
        Maximum extent of the aggregate in the x-direction.
        """
        return self._this.max_x
    @property
    def max_y(self):
        """Obtains the maximum y co-ordinate value of the aggregate.

        Returns
        -------
        Maximum extent of the aggregate in the y-direction.
        """
        return self._this.max_y
    @property
    def max_z(self):
        """Obtains the maximum z co-ordinate value of the aggregate.

        Returns
        -------
        Maximum extent of the aggregate in the z-direction.
        """
        return self._this.max_z
    @property
    def radius(self):
        """Returns the radius of the smallest sphere which bounds all
        particles in the aggregate.

        Returns
        -------
        Value of the radius of smallest bounding sphere.
        """
        return np.sqrt(self._this.max_r_sqd)
    @property
    def size(self):
        """Returns the size of the aggregate in terms of the total number
        of particles - including the initial attractor seed.

        Returns
        -------
        Size of the aggregate.
        """
        return LIBDRP.vector_size(self._this._aggregate)
    def fractal_dimension(self):
        """Computes the fractal dimension of the aggregate.

        Returns
        -------
        Dimension of the aggregate fractal.
        """
        return np.log(self.size)/np.log(self.radius)
    def as_ndarray(self):
        """Copies the internal (C) aggregate structure to a `np.ndarray`
        with `shape=(n, 3)` where `n` is the size of the aggregate.

        Returns
        -------
        An instance of `np.ndarray` containing aggregate particle co-ordinates.
        """
        _IntTriplet_ptr_t = POINTER(_IntTriplet)
        aggsize = LIBDRP.vector_size(self._this._aggregate)
        ret = np.zeros((aggsize, 3), dtype=int)
        for idx in np.arange(aggsize):
            addr = LIBDRP.vector_at(self._this._aggregate, c_size_t(idx))
            aggp = cast(addr, _IntTriplet_ptr_t).contents
            ret[idx][0] = aggp.x
            ret[idx][1] = aggp.y
            ret[idx][2] = aggp.z
        return ret
    def generate(self, nparticles, display_progress=True):
        """Generates an aggregate consisting of `nparticles`.

        Parameters
        ----------
        *nparticles* :: `int`

            Size of aggregate to generate.

        *display_progress* :: `bool`, optional, default = True

            Print progress bar to terminal.

        Exceptions
        ----------
        Raises `MemoryError` if a vector reallocation failure occurs.
        """
        retval = LIBDRP.aggregate_3d_generate(self._handle,
                                              c_size_t(nparticles),
                                              c_bool(display_progress))
        if retval == -1:
            raise MemoryError("vector reallocation failure occurred in aggregate_3d_generate.")
        # initialise colors for each particle in aggregate
        self.colors = np.zeros(nparticles+self._this.att_size, dtype=(float, 3))
        clrpr.blue_through_red(self.colors)
    def generate_stream(self, nparticles, display_progress=False):
        """Generator function for streaming aggregate data to a real-time plot.

        Parameters
        ----------
        *nparticles* :: `int`

            Size of aggregate to generate.

        *display_progress* :: `bool`, optional, default = False

            Print progress bar to terminal.

        Exceptions
        ----------
        Raises `MemoryError` if a vector reallocation failure occurs.
        """
        LIBDRP.aggregate_3d_lattice_collision.restype = c_bool
        LIBDRP.aggregate_3d_collision.restype = c_bool
        _IntTriplet_ptr_t = POINTER(_IntTriplet)
        rv_res = LIBDRP.aggregate_reserve(self._handle, c_size_t(nparticles))
        if rv_res == -1:
            raise MemoryError("vector reallocation failure occurred in aggregate_reserve.")
        rv_ia = LIBDRP.aggregate_3d_init_attractor(self._handle, c_size_t(nparticles))
        if rv_ia == -1:
            raise MemoryError("""vector reallocation failure occurred in
            aggregate_3d_init_attractor.""")
        self.__aggregate = np.zeros((nparticles + self._this.att_size, 3), dtype=int)
        # initialise colors for each particle in aggregate
        self.colors = np.zeros(2*(nparticles+self._this.att_size), dtype=(float, 3))
        clrpr.blue_through_red(self.colors)
        curr = _IntTriplet()
        prev = _IntTriplet()
        has_next_spawned = False
        rsteps = c_size_t(0)
        bcolls = c_size_t(0)
        count = 0
        if display_progress:
            pbar = pb.ProgressBar(maxval=nparticles).start()
        while count < nparticles:
            if not has_next_spawned:
                LIBDRP.aggregate_3d_spawn_bp(self._handle, byref(curr))
                has_next_spawned = True
            prev.x = curr.x
            prev.y = curr.y
            prev.z = curr.z
            LIBDRP.aggregate_3d_update_bp(self._handle, byref(curr))
            if LIBDRP.aggregate_3d_lattice_collision(self._handle, byref(curr), byref(prev)):
                bcolls = c_size_t(bcolls.value + 1)
            rsteps = c_size_t(rsteps.value + 1)
            if LIBDRP.aggregate_3d_collision(self._handle, byref(curr), byref(prev)):
                addr_rec = LIBDRP.vector_at(self._this._aggregate,
                                            c_size_t(count + self._this.att_size))
                aggp_rec = cast(addr_rec, _IntTriplet_ptr_t).contents
                self.__aggregate[count+self._this.att_size][0] = aggp_rec.x
                self.__aggregate[count+self._this.att_size][1] = aggp_rec.y
                self.__aggregate[count+self._this.att_size][2] = aggp_rec.z
                LIBDRP.vector_push_back(self._this._rsteps, byref(rsteps), sizeof(c_size_t))
                LIBDRP.vector_push_back(self._this._bcolls, byref(bcolls), sizeof(c_size_t))
                rsteps = c_size_t(0)
                bcolls = c_size_t(0)
                count += 1
                has_next_spawned = False
                if display_progress:
                    pbar.update(count)
                yield self.__aggregate, self.colors, count
        if display_progress:
            pbar.finish()
