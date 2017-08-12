#include "aggregate.h"
#include <stdio.h>

static inline double prand() { return (double)rand()/(double)RAND_MAX; }

struct aggregate_2d* aggregate_2d_alloc(void) {
    return malloc(sizeof(struct aggregate_2d));
}

void aggregate_2d_free(struct aggregate_2d* agg) {
    aggregate_2d_free_fields(agg);
    free(agg);
}

int aggregate_2d_init(struct aggregate_2d* agg, double stickiness) {
    agg->_aggregate = (struct vector*)NULL;
    agg->_attractor = (struct vector*)NULL;
    agg->_rsteps = (struct vector*)NULL;
    agg->_bcolls = (struct vector*)NULL;
    // try to allocate vectors
    agg->_aggregate = vector_alloc(sizeof(struct pair));
    if (!(agg->_aggregate)) goto errorcleanup;
    agg->_attractor = vector_alloc(sizeof(struct pair));
    if (!(agg->_attractor)) goto errorcleanup;
    agg->_rsteps = vector_alloc(sizeof(size_t));
    if (!(agg->_rsteps)) goto errorcleanup;
    agg->_bcolls = vector_alloc(sizeof(size_t));
    if (!(agg->_bcolls)) goto errorcleanup;
    agg->stickiness = stickiness;
    agg->max_x = 0U;
    agg->max_y = 0U;
    agg->max_r_sqd = agg->max_x*agg->max_x + agg->max_y*agg->max_y;
    agg->b_offset = 6U;
    agg->spawn_diam = agg->b_offset;
    agg->att_size = 1U;
    agg->lt = SQUARE;
    agg->at = POINT;
    srand(time(NULL));
    return 0;
    errorcleanup: // clean-up if memory allocation fails
        aggregate_2d_free_fields(agg);
        return -1;
}

void aggregate_2d_free_fields(struct aggregate_2d* agg) {
    if (agg->_aggregate) vector_free(agg->_aggregate);
    if (agg->_attractor) vector_free(agg->_attractor);
    if (agg->_rsteps) vector_free(agg->_rsteps);
    if (agg->_bcolls) vector_free(agg->_bcolls);
}

size_t aggregate_2d_size(const struct aggregate_2d* agg) {
    return vector_size(agg->_aggregate);
}

int aggregate_2d_reserve(struct aggregate_2d* agg, size_t n) {
    int ec1 = vector_reserve(agg->_rsteps, n);
    if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
    int ec2 = vector_reserve(agg->_bcolls, n);
    if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
    return 0;
}

int aggregate_2d_init_attractor(struct aggregate_2d* agg, size_t n) {
    if (agg->at == POINT) {
        agg->att_size = 1U;
        struct pair origin;
        origin.x = 0; origin.y = 0;
        int ec1 = vector_reserve(agg->_attractor, agg->att_size);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        int ec2 = vector_reserve(agg->_aggregate, n + agg->att_size);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        vector_push_back(agg->_attractor, &origin, sizeof origin);
        vector_push_back(agg->_aggregate, &origin, sizeof origin);
    }
    return 0;
}

void aggregate_2d_spawn_bp(const struct aggregate_2d* agg,
                           struct pair* curr) {
    const double ppr = prand(); // generate random number in [0, 1]
    if (agg->at == POINT) {
        if (ppr < 0.5) {
            curr->x = (int)(agg->spawn_diam*(prand() - 0.5));
            curr->y = (int)(ppr < 0.25 ? agg->spawn_diam*0.5 : -agg->spawn_diam*0.5);
        }
        else {
            curr->x = (int)(ppr < 0.75 ? agg->spawn_diam*0.5 : -agg->spawn_diam*0.5);
            curr->y = (int)(agg->spawn_diam*(prand() - 0.5));
        }
    }
}

void aggregate_2d_update_bp(const struct aggregate_2d* agg,
                            struct pair* curr) {
    const double md = prand();
    if (agg->lt == SQUARE) {
        if (md < 0.25) ++(curr->x);
        else if (md >= 0.25 && md < 0.5) --(curr->x);
        else if (md >= 0.5 && md < 0.75) ++(curr->y);
        else --(curr->y);
    }
}

bool aggregate_2d_lattice_collision(const struct aggregate_2d* agg,
                                    struct pair* curr,
                                    const struct pair* prev) {
    const int epsilon = 2;
    if (agg->at == POINT) {
        const int bnd_absmax = (int)(agg->spawn_diam*0.5 + epsilon);
        if (abs(curr->x) > bnd_absmax || abs(curr->y) > bnd_absmax) {
            curr->x = prev->x;
            curr->y = prev->y;
            return true;
        }
    }
    return false;
}

bool aggregate_2d_collision(struct aggregate_2d* agg,
                            struct pair* curr,
                            struct pair* prev) {
    if (prand() > agg->stickiness) return false;
    for (size_t i = 0U; i < vector_size(agg->_aggregate); ++i) {
        struct pair* aggp = (struct pair*)vector_at(agg->_aggregate, i);
        if (curr->x == aggp->x && curr->y == aggp->y) {
            vector_push_back(agg->_aggregate, prev, sizeof *prev);
            if (agg->at == POINT) {
                double rsqd = prev->x * prev->x + prev->y * prev->y;
                if (rsqd > agg->max_r_sqd) {
                    agg->max_r_sqd = rsqd;
                    agg->spawn_diam = 2*(int)(sqrt(rsqd)) + agg->b_offset;
                }
            }
            return true;
        }
    }
    return false;
}

int aggregate_2d_generate(struct aggregate_2d* agg, size_t n) {
    if (aggregate_2d_reserve(agg, n) == -1 ||
        aggregate_2d_init_attractor(agg, n) == -1) return -1;
    struct pair curr;
    struct pair prev;
    size_t steps_to_stick = 0U;
    size_t bcolls = 0U;
    size_t count = 0U;
    bool has_next_spawned = false;
    while (count < n) {
        if (!has_next_spawned) {
            aggregate_2d_spawn_bp(agg, &curr);
            has_next_spawned = true;
        }
        prev.x = curr.x;
        prev.y = curr.y;
        aggregate_2d_update_bp(agg, &curr);
        printf("curr.x = %d\n", curr.x);
        printf("curr.y = %d\n", curr.y);
        if (aggregate_2d_lattice_collision(agg, &curr, &prev)) ++bcolls;
        ++steps_to_stick;
        if (aggregate_2d_collision(agg, &curr, &prev)) {
            vector_push_back(agg->_rsteps, &steps_to_stick, sizeof steps_to_stick);
            vector_push_back(agg->_bcolls, &bcolls, sizeof bcolls);
            steps_to_stick = 0U;
            bcolls = 0U;
            ++count;
            //printf("count = %lu\n", count);
            has_next_spawned = false;
        }
    }
    return 0;
}
