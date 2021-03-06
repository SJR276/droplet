#include "aggregate.h"

static inline double prand() { return (double)rand()/(double)RAND_MAX; }

struct aggregate* aggregate_alloc(void) {
    return malloc(sizeof(struct aggregate));
}

void aggregate_free(struct aggregate* agg) {
    aggregate_free_fields(agg);
    free(agg);
}

void aggregate_free_fields(struct aggregate* agg) {
    if (agg->_aggregate) vector_free(agg->_aggregate);
    if (agg->_attractor) vector_free(agg->_attractor);
    if (agg->_rsteps) vector_free(agg->_rsteps);
    if (agg->_bcolls) vector_free(agg->_bcolls);
}

int aggregate_reserve(struct aggregate* agg, size_t n) {
    const int ec1 = vector_reserve(agg->_rsteps, n);
    if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
    const int ec2 = vector_reserve(agg->_bcolls, n);
    if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
    return 0;
}

/*** 2D aggregate functions ***/

int aggregate_2d_init(struct aggregate* agg,
    double stickiness,
    enum lattice_type lt,
    enum attractor_type at) {
    agg->_aggregate = (struct vector*)NULL;
    agg->_attractor = (struct vector*)NULL;
    agg->_rsteps = (struct vector*)NULL;
    agg->_bcolls = (struct vector*)NULL;
    // try to allocate vectors
    agg->_aggregate = vector_alloc(sizeof(struct int_pair));
    if (!(agg->_aggregate)) goto errorcleanup;
    agg->_attractor = vector_alloc(sizeof(struct int_pair));
    if (!(agg->_attractor)) goto errorcleanup;
    agg->_rsteps = vector_alloc(sizeof(size_t));
    if (!(agg->_rsteps)) goto errorcleanup;
    agg->_bcolls = vector_alloc(sizeof(size_t));
    if (!(agg->_bcolls)) goto errorcleanup;
    agg->stickiness = stickiness;
    agg->max_x = 0U;
    agg->max_y = 0U;
    agg->max_z = 0U;
    agg->max_r_sqd = agg->max_x*agg->max_x + agg->max_y*agg->max_y;
    agg->b_offset = 6U; // small offset from spawning region to lattice boundary
    agg->spawn_diam = agg->b_offset;
    agg->att_size = 1U;
    agg->lt = lt;
    agg->at = at;
    srand(time(NULL)); // seed PRNG
    return 0;
    errorcleanup: // clean-up if memory allocation fails
        aggregate_free_fields(agg);
        return -1;
}

int aggregate_2d_init_attractor(struct aggregate* agg, size_t n) {
    if (agg->at == POINT) { // set origin point
        struct int_pair origin;
        origin.x = 0; origin.y = 0;
        const int ec1 = vector_reserve(agg->_attractor, agg->att_size);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, n + agg->att_size);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        vector_push_back(agg->_attractor, &origin, sizeof origin);
        vector_push_back(agg->_aggregate, &origin, sizeof origin);
    }
    else if (agg->at == LINE) { // set (x=[-att_size/2, att_size/2], y=0)
        const int ec1 = vector_reserve(agg->_attractor, agg->att_size);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, n + agg->att_size);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        for (int i = 0; i < (int)agg->att_size; ++i) {
            struct int_pair attp;
            attp.x = i - (int)(0.5*agg->att_size);
            attp.y = 0;
            vector_push_back(agg->_attractor, &attp, sizeof attp);
            vector_push_back(agg->_aggregate, &attp, sizeof attp);
        }
    }
    else if (agg->at == CIRCLE) { // set circle with r = att_size
        const size_t attparticles = (size_t)(2.0*M_PI*agg->att_size) + 1U;
        const int ec1 = vector_reserve(agg->_attractor, attparticles);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, attparticles);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        const double step = 1.0/agg->att_size;
        for (double theta = 0.0; theta < 2.0*M_PI + step; theta += step) {
            struct int_pair attp;
            attp.x = (int)(agg->att_size*cos(theta));
            attp.y = (int)(agg->att_size*sin(theta));
            vector_push_back(agg->_attractor, &attp, sizeof attp);
            vector_push_back(agg->_aggregate, &attp, sizeof attp);
        }
    }
    return 0;
}

void aggregate_2d_spawn_bp(const struct aggregate* agg,
                           struct int_pair* curr) {
    const double ppr = prand();
    if (agg->at == POINT) {
        if (ppr < 0.5) { // positive/negative y-line of boundary
            curr->x = (int)agg->spawn_diam*(prand() - 0.5);
            curr->y = (ppr < 0.25) ? (int)(agg->spawn_diam*0.5) : -(int)(agg->spawn_diam*0.5);
        }
        else { // positive/negative x-line of boundary
            curr->x = (ppr < 0.75) ? (int)(agg->spawn_diam*0.5) : -(int)(agg->spawn_diam*0.5);
            curr->y = (int)agg->spawn_diam*(prand() - 0.5);
        }
    }
    else if (agg->at == LINE) {
        curr->x = 2*(int)(agg->att_size*(prand() - 0.5));
        curr->y = (ppr < 0.5) ? (int)agg->spawn_diam : -(int)agg->spawn_diam;
    }
}

void aggregate_2d_update_bp(const struct aggregate* agg,
                            struct int_pair* curr) {
    const double md = prand();
    if (agg->lt == SQUARE) {
        if (md < 0.25) ++(curr->x);
        else if (md >= 0.25 && md < 0.5) --(curr->x);
        else if (md >= 0.5 && md < 0.75) ++(curr->y);
        else --(curr->y);
    }
    else if (agg->lt == TRIANGLE) {
        if (md < 1.0/6.0) ++(curr->x);
        else if (md >= 1.0/6.0 && md < 2.0/6.0) --(curr->x);
        else if (md >= 2.0/6.0 && md < 3.0/6.0) {
            ++(curr->x);
            ++(curr->y);
        }
        else if (md >= 3.0/6.0 && md < 4.0/6.0) {
            ++(curr->x);
            --(curr->y);
        }
        else if (md >= 4.0/6.0 && md < 5.0/6.0) {
            --(curr->x);
            ++(curr->y);
        }
        else {
            --(curr->x);
            --(curr->y);
        }
    }
}

bool aggregate_2d_lattice_collision(const struct aggregate* agg,
                                    struct int_pair* curr,
                                    const struct int_pair* prev) {
    const int epsilon = 2; // small elastic boundary correction
    if (agg->at == POINT || agg->at == CIRCLE) {
        const int bnd_absmax = (int)(agg->spawn_diam*0.5 + epsilon);
        if (abs(curr->x) > bnd_absmax || abs(curr->y) > bnd_absmax) {
            curr->x = prev->x;
            curr->y = prev->y;
            return true;
        }
    }
    if (agg->at == LINE) {
        if (abs(curr->x) > 2*(int)agg->att_size ||
            abs(curr->y) > (int)agg->spawn_diam + epsilon) {
            curr->x = prev->x;
            curr->y = prev->y;
        }
    }
    return false;
}

bool aggregate_2d_collision(struct aggregate* agg,
                            struct int_pair* curr,
                            struct int_pair* prev) {
    if (prand() > agg->stickiness) return false;
    for (size_t i = 0U; i < vector_size(agg->_aggregate); ++i) {
        const struct int_pair* aggp = (struct int_pair*)vector_at(agg->_aggregate, i);
        if (curr->x == aggp->x && curr->y == aggp->y) {
            vector_push_back(agg->_aggregate, prev, sizeof *prev);
            if (abs(prev->x) > agg->max_x) agg->max_x = abs(prev->x);
            bool expand_spawn_line = false;
            if (abs(prev->y) > agg->max_y) {
                agg->max_y = abs(prev->y);
                expand_spawn_line = true;
            }
            // expand spawning region if necessary
            if (agg->at == POINT) {
                double rsqd = prev->x * prev->x + prev->y * prev->y;
                if (rsqd > agg->max_r_sqd) {
                    agg->max_r_sqd = rsqd;
                    agg->spawn_diam = 2*(int)(sqrt(rsqd)) + agg->b_offset;
                }
            }
            else if (agg->at == LINE && expand_spawn_line)
                agg->spawn_diam = prev->y + agg->b_offset;
            return true;
        }
    }
    return false;
}

int aggregate_2d_generate(struct aggregate* agg, size_t n, bool disp_prog) {
    if (aggregate_reserve(agg, n) == -1 ||
        aggregate_2d_init_attractor(agg, n) == -1) return -1;
    struct int_pair curr;
    struct int_pair prev;
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
        if (aggregate_2d_lattice_collision(agg, &curr, &prev)) ++bcolls;
        ++steps_to_stick;
        if (aggregate_2d_collision(agg, &curr, &prev)) {
            vector_push_back(agg->_rsteps, &steps_to_stick, sizeof steps_to_stick);
            vector_push_back(agg->_bcolls, &bcolls, sizeof bcolls);
            steps_to_stick = 0U;
            bcolls = 0U;
            ++count;
            if (disp_prog) {
                printf("\rProgress: %d%%", (int)(100*(double)count/(double)n));
                fflush(stdout);
            }
            has_next_spawned = false;
        }
    }
    return 0;
}

/*** 3D aggregate functions ***/

int aggregate_3d_init(struct aggregate* agg,
    double stickiness,
    enum lattice_type lt,
    enum attractor_type at) {
    agg->_aggregate = (struct vector*)NULL;
    agg->_attractor = (struct vector*)NULL;
    agg->_rsteps = (struct vector*)NULL;
    agg->_bcolls = (struct vector*)NULL;
    // try to allocate vectors
    agg->_aggregate = vector_alloc(sizeof(struct int_triplet));
    if (!(agg->_aggregate)) goto errorcleanup;
    agg->_attractor = vector_alloc(sizeof(struct int_triplet));
    if (!(agg->_attractor)) goto errorcleanup;
    agg->_rsteps = vector_alloc(sizeof(size_t));
    if (!(agg->_rsteps)) goto errorcleanup;
    agg->_bcolls = vector_alloc(sizeof(size_t));
    if (!(agg->_bcolls)) goto errorcleanup;
    agg->stickiness = stickiness;
    agg->max_x = 0U;
    agg->max_y = 0U;
    agg->max_z = 0U;
    agg->max_r_sqd = agg->max_x*agg->max_x + agg->max_y*agg->max_y
        + agg->max_z*agg->max_z;
    agg->b_offset = 6U;
    agg->spawn_diam = agg->b_offset;
    agg->att_size = 1U;
    agg->lt = lt;
    agg->at = at;
    srand(time(NULL));
    return 0;
    errorcleanup:
        aggregate_free_fields(agg);
        return -1;
}

int aggregate_3d_init_attractor(struct aggregate* agg, size_t n) {
    if (agg->at == POINT) { // set origin point
        struct int_triplet origin;
        origin.x = 0; origin.y = 0; origin.z = 0;
        const int ec1 = vector_reserve(agg->_attractor, agg->att_size);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, n + agg->att_size);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        vector_push_back(agg->_attractor, &origin, sizeof origin);
        vector_push_back(agg->_aggregate, &origin, sizeof origin);
    }
    else if (agg->at == LINE) { // set (x=[-att_size/2, att_size/2], y=0, z=0)
        const int ec1 = vector_reserve(agg->_attractor, agg->att_size);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, n + agg->att_size);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        for (int i = 0; i < (int)agg->att_size; ++i) {
            struct int_triplet attp;
            attp.x = i - (int)(0.5*agg->att_size);
            attp.y = 0; attp.z = 0;
            vector_push_back(agg->_attractor, &attp, sizeof attp);
            vector_push_back(agg->_aggregate, &attp, sizeof attp);
        }
    }
    // set (x=[-att_size/2, att_size/2], y=[-att_size/2, att_size/2], z=0)
    else if (agg->at == PLANE) {
        const size_t attparticles = agg->att_size*agg->att_size;
        const int ec1 = vector_reserve(agg->_attractor, attparticles);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, n + attparticles);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        for (int i = 0; i < (int)agg->att_size; ++i) {
            for (int j = 0; j < (int)agg->att_size; ++j) {
                struct int_triplet attp;
                attp.x = i - (int)(0.5*agg->att_size);
                attp.y = j - (int)(0.5*agg->att_size);
                attp.z = 0;
                vector_push_back(agg->_attractor, &attp, sizeof attp);
                vector_push_back(agg->_aggregate, &attp, sizeof attp);
            }
        }
    }
    else if (agg->at == CIRCLE) { // set circle with r = att_size
        const size_t attparticles = (size_t)(2.0*M_PI*agg->att_size) + 1U;
        const int ec1 = vector_reserve(agg->_attractor, attparticles);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, attparticles);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        const double step = 1.0/agg->att_size;
        for (double theta = 0.0; theta < 2.0*M_PI + step; theta += step) {
            struct int_triplet attp;
            attp.x = (int)(agg->att_size*cos(theta));
            attp.y = (int)(agg->att_size*sin(theta));
            attp.z = 0;
            vector_push_back(agg->_attractor, &attp, sizeof attp);
            vector_push_back(agg->_aggregate, &attp, sizeof attp);
        }
    }
    else if (agg->at == SPHERE) { // set sphere with r = att_size
        const size_t attparticles = (size_t)((2*M_PI*agg->att_size + 1)*(M_PI*agg->att_size + 1));
        const int ec1 = vector_reserve(agg->_attractor, attparticles);
        if (ec1 == VECTOR_REALLOC_FAILURE) return -1;
        const int ec2 = vector_reserve(agg->_aggregate, attparticles);
        if (ec2 == VECTOR_REALLOC_FAILURE) return -1;
        const double step = 1.0/agg->att_size;
        for (double phi = 0.0; phi < 2.0*M_PI + step; phi += step) { // azimuthal
            for (double theta = -0.5*M_PI; theta < 0.5*M_PI + step; theta += step) { // polar
                struct int_triplet attp;
                attp.x = (int)(agg->att_size*sin(theta)*cos(phi));
                attp.y = (int)(agg->att_size*sin(theta)*sin(phi));
                attp.z = (int)(agg->att_size*cos(theta));
                vector_push_back(agg->_attractor, &attp, sizeof attp);
                vector_push_back(agg->_aggregate, &attp, sizeof attp);
            }
        }
    }
    return 0;
}

void aggregate_3d_spawn_bp(const struct aggregate* agg,
    struct int_triplet* curr) {
    const double ppr = prand();
    if (agg->at == POINT) {
        if (ppr < 1.0/3.0) { // positive/negative z-plane of boundary
            curr->x = (int)(agg->spawn_diam*(prand() - 0.5));
            curr->y = (int)(agg->spawn_diam*(prand() - 0.5));
            curr->z = (ppr < 1.0/6.0) ? (int)(agg->spawn_diam*0.5) : -(int)(agg->spawn_diam*0.5);
        }
        else if (ppr >= 1.0/3.0 && ppr < 2.0/3.0) { // positive/negative x-plane of boundary
            curr->x = (ppr < 0.5) ? (int)(agg->spawn_diam*0.5) : -(int)(agg->spawn_diam*0.5);
            curr->y = (int)(agg->spawn_diam*(prand() - 0.5));
            curr->z = (int)(agg->spawn_diam*(prand() - 0.5));
        }
        else { // positive/negative z-plane of boundary
            curr->x = (int)(agg->spawn_diam*(prand() - 0.5));
            curr->y = (ppr < 5.0/6.0) ? (int)(agg->spawn_diam*0.5) : -(int)(agg->spawn_diam*0.5);
            curr->z = (int)(agg->spawn_diam*(prand() - 0.5));
        }
    }
    else if (agg->at == LINE) {
        curr->x = 2*(int)(agg->att_size*(prand() - 0.5));
        curr->y = (ppr < 0.5) ? (int)agg->spawn_diam : -(int)agg->spawn_diam;
        curr->z = (ppr < 0.5) ? (int)agg->spawn_diam : -(int)agg->spawn_diam;
    }
    else if (agg->at == PLANE) {
        curr->x = 2*(int)(agg->att_size*(prand() - 0.5));
        curr->y = 2*(int)(agg->att_size*(prand() - 0.5));
        curr->z = (ppr < 0.5) ? (int)agg->spawn_diam : - (int)agg->spawn_diam;
    }
}

void aggregate_3d_update_bp(const struct aggregate* agg,
    struct int_triplet* curr) {
    const double md = prand();
    if (agg->lt == SQUARE) {
        if (md < 1.0/6.0) ++(curr->x);
        else if (md >= 1.0/6.0 && md < 2.0/6.0) --(curr->x);
        else if (md >= 2.0/6.0 && md < 3.0/6.0) ++(curr->y);
        else if (md >= 3.0/6.0 && md < 4.0/6.0) --(curr->y);
        else if (md >= 4.0/6.0 && md < 5.0/6.0) ++(curr->z);
        else --(curr->z);
    }
    else if (agg->lt == TRIANGLE) {
        if (md < 1.0/8.0) {
            ++(curr->x);
            ++(curr->y);
        }
        else if (md >= 1.0/8.0 && md < 2.0/8.0) {
            ++(curr->x);
            --(curr->y);
        }
        else if (md >= 2.0/8.0 && md < 3.0/8.0) {
            --(curr->x);
            --(curr->y);
        }
        else if (md >= 3.0/8.0 && md < 4.0/8.0) {
            --(curr->x);
            ++(curr->y);
        }
        else if (md >= 4.0/8.0 && md < 5.0/8.0) ++(curr->x);
        else if (md >= 5.0/8.0 && md < 6.0/8.0) --(curr->x);
        else if (md >= 6.0/8.0 && md < 7.0/8.0) ++(curr->z);
        else --(curr->z);
    }
}

bool aggregate_3d_lattice_collision(const struct aggregate* agg,
    struct int_triplet* curr,
    const struct int_triplet* prev) {
    const int epsilon = 2;
    if (agg->at == POINT || agg->at == CIRCLE || agg->at == SPHERE) {
        const int bnd_absmax = (int)(agg->spawn_diam*0.5) + epsilon;
        if (abs(curr->x) > bnd_absmax || abs(curr->y) > bnd_absmax
            || abs(curr->z) > bnd_absmax) {
            curr->x = prev->x;
            curr->y = prev->y;
            curr->z = prev->z;
            return true;
        }
    }
    else if (agg->at == LINE) {
        if (abs(curr->x) > 2*(int)agg->att_size ||
            abs(curr->y) > (int)agg->spawn_diam + epsilon ||
            abs(curr->z) > (int)agg->spawn_diam + epsilon) {
            curr->x = prev->x;
            curr->y = prev->y;
            curr->z = prev->z;
            return true;
        }
    }
    else if (agg->at == PLANE) {
        if (abs(curr->x) > 2*(int)agg->att_size ||
            abs(curr->y) > 2*(int)agg->att_size ||
            abs(curr->z) > (int)agg->spawn_diam + epsilon) {
            curr->x = prev->x;
            curr->y = prev->y;
            curr->z = prev->z;
            return true;
        }
    }
    return false;
}

bool aggregate_3d_collision(struct aggregate* agg,
    struct int_triplet* curr,
    struct int_triplet* prev) {
    if (prand() > agg->stickiness) return false;
    for (size_t i = 0U; i < vector_size(agg->_aggregate); ++i) {
        const struct int_triplet* aggp = (struct int_triplet*)vector_at(agg->_aggregate, i);
        if (curr->x == aggp->x && curr->y == aggp->y && curr->z == aggp->z) {
            vector_push_back(agg->_aggregate, prev, sizeof *prev);
            if (abs(prev->x) > agg->max_x) agg->max_x = abs(prev->x);
            if (abs(prev->y) > agg->max_y) agg->max_y = abs(prev->y);
            bool expand_spawn_plane = false;
            if (abs(prev->z) > agg->max_z) { 
                agg->max_z = abs(prev->z);
                expand_spawn_plane = true;
            }
            // expand spawning region if necessary
            if (agg->at == POINT) {
                double rsqd = prev->x*prev->x + prev->y*prev->y + prev->z*prev->z;
                if (rsqd > agg->max_r_sqd) {
                    agg->max_r_sqd = rsqd;
                    agg->spawn_diam = 2*(int)(sqrt(rsqd)) + agg->b_offset;
                }
            }
            else if (agg->at == PLANE && expand_spawn_plane)
                agg->spawn_diam = prev->z + agg->b_offset;
            return true;
        }
    }
    return false;
}

int aggregate_3d_generate(struct aggregate* agg, size_t n, bool disp_prog) {
    if (aggregate_reserve(agg, n) == -1 ||
        aggregate_3d_init_attractor(agg, n) == -1) return -1;
    struct int_triplet curr;
    struct int_triplet prev;
    size_t steps_to_stick = 0U;
    size_t bcolls = 0U;
    size_t count = 0U;
    bool has_next_spawned = false;
    while (count < n) {
        if (!has_next_spawned) {
            aggregate_3d_spawn_bp(agg, &curr);
            has_next_spawned = true;
        }
        prev.x = curr.x;
        prev.y = curr.y;
        prev.z = curr.z;
        aggregate_3d_update_bp(agg, &curr);
        if (aggregate_3d_lattice_collision(agg, &curr, &prev)) ++bcolls;
        ++steps_to_stick;
        if (aggregate_3d_collision(agg, &curr, &prev)) {
            vector_push_back(agg->_rsteps, &steps_to_stick, sizeof steps_to_stick);
            vector_push_back(agg->_bcolls, &bcolls, sizeof bcolls);
            steps_to_stick = 0U;
            bcolls = 0U;
            ++count;
            if (disp_prog) {
                printf("\rProgress: %d%%", (int)(100*(double)count/(double)n));
                fflush(stdout);
            }
            has_next_spawned = false;
        }
    }
    return 0;
}
