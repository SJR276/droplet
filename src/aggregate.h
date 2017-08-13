#ifndef AGGREGATE_H_
#define AGGREGATE_H_

#include "vector.h"
#include <math.h>
#include <stdio.h>
#include <time.h>

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

struct triplet {
    int x;
    int y;
    int z;
};

struct aggregate {
    struct vector* _aggregate; /**< Aggregate particle co-ordinates. */
    struct vector* _attractor; /**< Attractor particle co-ordinates. */
    struct vector* _bcolls; /**< Lattice boundary collisions beffore stick for each particle. */
    struct vector* _rsteps; /**< Required steps until stick for each particle. */
    double stickiness; /**< Probability of a particle sticking to the aggregate. */
    size_t max_x; /**< Maximum extent of aggregate in x-direction. */
    size_t max_y; /**< Maximum extent of aggregate in y-direction. */
    size_t max_z; /**< Maximum extent of aggregate in z-direction. */
    size_t max_r_sqd; /**< Current maximum radius squared of aggregate. */
    size_t b_offset; /**< Boundary offset for spawning region. */
    size_t spawn_diam; /**< Spawning region diameter. */
    size_t att_size; /**< Number of particles in attractor. */
    enum lattice_type lt; /**< Type of lattice to generate aggregate upon. */
    enum attractor_type at; /**< Type of initial attractor geometry. */
};

struct aggregate* aggregate_alloc(void);

void aggregate_free(struct aggregate* agg);

int aggregate_2d_init(struct aggregate* agg,
                      double stickiness,
                      enum lattice_type lt,
                      enum attractor_type at);
int aggregate_3d_init(struct aggregate* agg,
                      double stickiness,
                      enum lattice_type lt,
                      enum attractor_type at);

void aggregate_free_fields(struct aggregate* agg);

int aggregate_reserve(struct aggregate* agg, size_t n);

int aggregate_2d_init_attractor(struct aggregate* agg, size_t n);
int aggregate_3d_init_attractor(struct aggregate* agg, size_t n);

void aggregate_2d_spawn_bp(const struct aggregate* agg,
                           struct pair* curr);
void aggregate_3d_spawn_bp(const struct aggregate* agg,
                           struct triplet* curr);

void aggregate_2d_update_bp(const struct aggregate* agg, 
                            struct pair* curr);
void aggregate_3d_update_bp(const struct aggregate* agg,
                            struct triplet* curr);

bool aggregate_2d_lattice_collision(const struct aggregate* agg,
                                    struct pair* curr,
                                    const struct pair* prev);
bool aggregate_3d_lattice_collision(const struct aggregate* agg,
                                    struct triplet* curr,
                                    const struct triplet* prev);

bool aggregate_2d_collision(struct aggregate* agg,
                            struct pair* curr,
                            struct pair* prev);
bool aggregate_3d_collision(struct aggregate* agg,
                            struct triplet* curr,
                            struct triplet* prev);

int aggregate_2d_generate(struct aggregate* agg, size_t n, bool disp_prog);
int aggregate_3d_generate(struct aggregate* agg, size_t n, bool disp_prog);

#endif // !AGGREGATE_H_