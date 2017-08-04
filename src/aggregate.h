#ifndef AGGREGATE_H_
#define AGGREGATE_H_
#include "vector.h"
#include <math.h>

enum lattice_type {
    SQUARE,
    TRIANGLE
};

enum attractor_type {
    POINT,
    CIRCLE,
    SPHERE,
    LINE,
    PLANE
};

struct pair {
    int x;
    int y;
};

struct aggregate_2d {
    struct vector* _aggregate;
    struct vector* _attractor;
    struct vector* _bcolls; /**< Lattice boundary collisions beffore stick for each particle. */
    struct vector* _rsteps; /**< Required steps until stick for each particle. */
    double stickiness;
    size_t max_x;
    size_t max_y;
    size_t max_r_sqd; /**< Current maximum radius squared of aggregate. */
    size_t b_offset; /**< Boundary offset for spawning region. */
    size_t spawn_diam;
    size_t att_size; /**< Number of particles in attractor. */
    enum lattice_type lt;
    enum attractor_type at;
};

struct aggregate_2d* aggregate_2d_alloc(void);

void aggregate_2d_free(struct aggregate_2d* agg);

int aggregate_2d_init(struct aggregate_2d* agg, double stickiness);

void aggregate_2d_free_fields(struct aggregate_2d* agg);

size_t aggregate_2d_size(const struct aggregate_2d* agg);

int aggregate_2d_reserve(struct aggregate_2d* agg, size_t n);

void aggregate_2d_spawn_bp(const struct aggregate_2d* agg,
                           struct pair* curr);

void aggregate_2d_update_bp(const struct aggregate_2d* agg, 
                            struct pair* curr);

bool aggregate_2d_lattice_collision(const struct aggregate_2d* agg,
                                    struct pair* curr,
                                    const struct pair* prev);

bool aggregate_2d_collision(struct aggregate_2d* agg,
                            struct pair* curr,
                            struct pair* prev);

int aggregate_2d_generate(struct aggregate_2d* agg, size_t n);

struct pair aggregate_2d_particle_at(const struct aggregate_2d* agg, size_t idx);

#endif // !AGGREGATE_H_