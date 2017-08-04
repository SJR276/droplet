/**
 * \file vector.c
 * \author Samuel Rowlinson
 * \date 21 March 2017
 * \brief Contains the implementation of all functions declared in
 *        vector.h.
 */

#include "vector.h"

/**
 * \brief Reallocates a vector instance to a new memory store. To be used
 *        only internally by the vector. If `cpty < vec->capacity` then
 *        `vec->data` is reallocated to a new memory block where only the
 *         first `cpty` elements remain.
 * \param vec Instance of vector to reallocate.
 * \param cpty Capacity to allocate.
 */
int private_vector_reallocate(struct vector* vec, size_t cpty);

struct vector* vector_alloc(size_t elemsize) {
    // allocate memory for an empty vector
    struct vector* vec = malloc(sizeof(struct vector));
    if (!vec) return vec;
    vec->capacity = 8U; 
    vec->elemsize = elemsize;
    vec->size = 0U;
    // dynamically allocate char array corresponding 
    // to element size and capacity of vector
    vec->data = malloc(vec->capacity * vec->elemsize);
    if (!(vec->data)) { free(vec); vec = (struct vector*)NULL; }
    return vec;
}

void vector_free(struct vector* vec) {
    free(vec->data);
    free(vec);
}

int private_vector_reallocate(struct vector* vec, size_t cpty) {
    if (cpty == vec->capacity) return VECTOR_REALLOC_PASS;
    unsigned char* tmp = realloc(vec->data, cpty * vec->elemsize);
    if (tmp) {
        vec->data = tmp;
        vec->capacity = cpty; // update new capacity
        return VECTOR_REALLOC_SUCCESS;
    }
    return VECTOR_REALLOC_FAILURE;
}

int vector_push_back(struct vector* vec, void* value, size_t elemsize) {
    assert(elemsize == vec->elemsize);
    // perform reallocation when size hits current capacity
    if (vec->size == vec->capacity) { 
        if (private_vector_reallocate(vec, vec->capacity*2U) == VECTOR_REALLOC_FAILURE)
            return -1;
    }
    // copy value to end of vector
    memcpy(vec->data + vec->size * vec->elemsize, (unsigned char*)value, vec->elemsize);
    ++(vec->size);
    return 1;
}

int vector_reserve(struct vector* vec, size_t cap) {
    if (cap > vec->capacity) return private_vector_reallocate(vec, cap);
    return VECTOR_REALLOC_PASS;
}

int vector_shrink_to_fit(struct vector* vec) {
    return private_vector_reallocate(vec, vec->size); // reallocate to size capacity
}

int vector_resize_shrink(struct vector* vec, size_t size) {
    assert(size <= vec->size);
    if (size == vec->size) return VECTOR_RESIZE_PASS;
    unsigned char* data = malloc(vec->capacity * vec->elemsize);
    if (!data) return VECTOR_RESIZE_FAILURE;
    memcpy(data, vec->data, size*vec->elemsize);
    free(vec->data);
    vec->data = data;
    vec->size = size;
    return VECTOR_RESIZE_SUCCESS;
}

int vector_resize_grow(struct vector* vec, size_t size, void* value, size_t elemsize) {
    assert(size >= vec->size);
    if (size == vec->size) return VECTOR_RESIZE_PASS;
    // reserve extra reqd space
    if (vector_reserve(vec, size) == VECTOR_REALLOC_FAILURE)
        return VECTOR_RESIZE_FAILURE;
    const size_t curr_size = vec->size;
    // push back (size - curr_size) elements of value
    for (size_t i = 0U; i < size - curr_size; ++i)
        vector_push_back(vec, value, elemsize);
    return VECTOR_RESIZE_SUCCESS;
}

size_t vector_size(const struct vector* vec) {
    return vec->size;
}

size_t vector_capacity(const struct vector* vec) {
    return vec->capacity;
}

void* vector_at(const struct vector* vec, size_t index) {
    return (void*)(vec->data + index * vec->elemsize);
}

bool vector_empty(const struct vector* vec) {
    return !(bool)vec->size;
}
