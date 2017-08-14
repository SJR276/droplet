import sys
sys.path.append("../")
import droplet as drp
from droplet.plotting import plot_aggregate3d
from droplet.realtime import RealTimeAggregate3D

def point_attractor_test(nparticles, lattice_type, stickiness=1.0):
    point_agg = drp.Aggregate3D(stickiness=stickiness,
                                lattice_type=lattice_type)
    point_agg.generate(nparticles)
    plot_aggregate3d(point_agg)

def plane_attractor_test(nparticles, lattice_type, attside=10, stickiness=1.0):
    plane_agg = drp.Aggregate3D(stickiness=stickiness,
                                lattice_type=lattice_type,
                                attractor_type=drp.AttractorType.PLANE)
    plane_agg.attractor_size = attside
    plane_agg.generate(nparticles)
    plot_aggregate3d(plane_agg)

def real_time_test(nparticles, lattice_type, stickiness=1.0, blitting=True,
                   save=False, filename=None, autorotate=False):
    agg_rt = drp.Aggregate3D(stickiness=stickiness,
                             lattice_type=lattice_type)
    return RealTimeAggregate3D(agg_rt, nparticles, blitting=blitting,
                               autorotate=autorotate, save=save,
                               filename=filename)

point_attractor_test(2000, drp.LatticeType.TRIANGLE)
#plane_attractor_test(2000, drp.LatticeType.SQUARE)
#real_time_test(1000, drp.LatticeType.TRIANGLE)
