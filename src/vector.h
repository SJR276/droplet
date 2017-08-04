/**
 * \file vector.h
 * \author Samuel Rowlinson
 * \date 21 March 2017
 * \brief File containing the vector struct definition and relevant
 *        API functions for manipulating vector instances.
 */

#ifndef VECTOR_H_
#define VECTOR_H_
#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
// vector error/notify codes
#define VECTOR_REALLOC_FAILURE -1
#define VECTOR_REALLOC_PASS 0
#define VECTOR_REALLOC_SUCCESS 1
#define VECTOR_RESIZE_FAILURE -1
#define VECTOR_RESIZE_PASS 0
#define VECTOR_RESIZE_SUCCESS 1

/**
 * \struct vector
 * \brief Structure mimicking a c++ style `std::vector`.
 */
struct vector {
    unsigned char* data; /**< Pointer to underlying data array. */
    size_t size; /**< Number of elements in the container. */
    size_t elemsize; /**< Size of the value type of the container in bytes. */
    size_t capacity; /**< Number of elements that can be held in currently allocated storage. */
};
/**
 * \brief Construct a new vector where the elements have a memory size
 *        given by `elemsize`.
 * \param elemsize Size in memory of type to store in vector (in bytes).
 * \return Pointer to newly allocated vector, `NULL` if malloc failed.
 */
struct vector* vector_alloc(size_t elemsize);
/**
 * \brief Destroy a vector instance, freeing its memory.
 * \param vec Pointer to instance of vector to delete.
 */
void vector_free(struct vector* vec);
/**
 * \brief Push a new value of memory size `elemsize` to the back of a vector
 *        instance. The `elemsize` value must equal the internal element size
 *        of types for the vector `vec`.
 * \param vec Pointer to instance of vector to push value to.
 * \param value Value to push back.
 * \param elemsize Size of `value` in memory (in bytes).
 * \return 1 if push back was successful, -1 otherwise.
 */
int vector_push_back(struct vector* vec, void* value, size_t elemsize);
/**
 * \brief Increases the capacity of a vector instance to a value `cap`. If 
 *        `cap > vec->capacity` then new storage is allocated, otherwise
 *        this method does nothing.
 * \param vec Pointer to instance of vector to reserve memory for.
 * \param cap New capacity for vector.
 * \return - `VECTOR_REALLOC_SUCCESS` if reserve was successful,
 *         - `VECTOR_REALLOC_PASS` if reserve was avoided.
 *         - `VECTOR_REALLOC_FAILURE` if reserve failed.
 */
int vector_reserve(struct vector* vec, size_t cap);
/**
 * \brief Reduces the capacity of a vector to the size of the vector.
 * \param vec Pointer to instance of vector to capacity shrink.
 * \return - `VECTOR_REALLOC_SUCCESS` if reserve was successful,
 *         - `VECTOR_REALLOC_PASS` if reserve was avoided.
 *         - `VECTOR_REALLOC_FAILURE` if reserve failed.
 */
int vector_shrink_to_fit(struct vector* vec);
/**
 * \brief Resizes a vector to contain `size` elements, where `size < vec->size`. The
 *        vector `vec` is reduced to its first `size` elements. 
 * \remark This method does *not* reduce the capacity of `vec`, to reduce the capacity
 *         after resizing use `vector_shrink_to_fit`.
 * \param vec Pointer to instance of vector to resize.
 * \param size New size of vector.
 * \return - `VECTOR_RESIZE_SUCCESS` if shrink was successful.
 *         - `VECTOR_RESIZE_PASS` if shrink was avoided.
 *         - `VECTOR_RESIZE_FAILURE` if shrink failed.
 */
int vector_resize_shrink(struct vector* vec, size_t size);
/**
 * \brief Resizes a vector to contain `size` elements, where `size > vec->size`. The
 *        vector `vec` is expanded to contain `size` elements where any extra elements
 *        are initialised with copies of `value`.
 * \param vec Pointer to instance of vector to resize.
 * \param size New size of vector.
 * \param value Value to initialise appended elements to.
 * \param elemsize Size of `value` in memory (in bytes).
 * \return - `VECTOR_RESIZE_SUCCESS` if grow was successful.
 *         - `VECTOR_RESIZE_PASS` if grow was avoided.
 *         - `VECTOR_RESIZE_FAILURE` if grow failed.
 */
int vector_resize_grow(struct vector* vec, size_t size, void* value, size_t elemsize);
/**
 * \brief Returns the size of a vector in terms of number of elements it currently contains.
 * \param vec Pointer to instance of vector to get size of.
 * \return Number of elements held by the vector.
 */
size_t vector_size(const struct vector* vec);
/**
 * \brief Returns the capacity of a vector, i.e. the number of elements it can hold before
 *        a re-allocation occurs. 
 * \param vec Pointer to instance of vector to get capacity of.
 * \return Capacity of the vector `vec`.
 */
size_t vector_capacity(const struct vector* vec);
/**
 * \brief Returns the `(void*)` cast element at the specified `index` of a vector.
 * \param vec Pointer to instance of vector.
 * \param index Index of element to access.
 * \return A void-pointer cast of the element at the specified index.
 */
void* vector_at(const struct vector* vec, size_t index);
/**
 * \brief Determines whether a vector `vec` is empty or not.
 * \param vec Pointer to instance of vector.
 * \return `true` if `vec` contains no elements, `false` otherwise.
 */
bool vector_empty(const struct vector* vec);

#endif // !VECTOR_H_ 
