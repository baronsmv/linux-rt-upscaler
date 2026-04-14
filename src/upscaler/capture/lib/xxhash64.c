/**
 * @file xxhash64.c
 * @brief xxHash64 implementation (embedded).
 */

#include "xxhash64.h"
#include <string.h>

#define XXH_PRIME64_1 11400714785074694791ULL
#define XXH_PRIME64_2 14029467366897019727ULL
#define XXH_PRIME64_3  1609587929392839161ULL
#define XXH_PRIME64_4  9650029242287828579ULL
#define XXH_PRIME64_5  2870177450012600261ULL

static inline unsigned long long XXH64_rotl(unsigned long long x, int r) {
    return (x << r) | (x >> (64 - r));
}

void XXH64_reset(XXH64_state_t *state, unsigned long long seed) {
    state->v1 = seed + XXH_PRIME64_1 + XXH_PRIME64_2;
    state->v2 = seed + XXH_PRIME64_2;
    state->v3 = seed;
    state->v4 = seed - XXH_PRIME64_1;
    state->total_len = 0;
    state->memsize = 0;
}

void XXH64_update(XXH64_state_t *state, const void *input, size_t len) {
    const unsigned char *p = (const unsigned char *)input;
    state->total_len += len;

    if (state->memsize + len < 32) {
        memcpy(state->mem + state->memsize, p, len);
        state->memsize += len;
        return;
    }

    if (state->memsize) {
        size_t fill = 32 - state->memsize;
        memcpy(state->mem + state->memsize, p, fill);
        p += fill; len -= fill;
        unsigned long long *m = (unsigned long long *)state->mem;
        state->v1 = XXH64_rotl(state->v1 + m[0] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v2 = XXH64_rotl(state->v2 + m[1] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v3 = XXH64_rotl(state->v3 + m[2] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v4 = XXH64_rotl(state->v4 + m[3] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->memsize = 0;
    }

    while (len >= 32) {
        unsigned long long m0, m1, m2, m3;
        memcpy(&m0, p, 8); memcpy(&m1, p+8, 8);
        memcpy(&m2, p+16, 8); memcpy(&m3, p+24, 8);
        state->v1 = XXH64_rotl(state->v1 + m0 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v2 = XXH64_rotl(state->v2 + m1 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v3 = XXH64_rotl(state->v3 + m2 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v4 = XXH64_rotl(state->v4 + m3 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        p += 32; len -= 32;
    }

    if (len) {
        memcpy(state->mem, p, len);
        state->memsize = len;
    }
}

unsigned long long XXH64_digest(XXH64_state_t *state) {
    unsigned long long h64;
    if (state->total_len >= 32) {
        h64 = XXH64_rotl(state->v1, 1) + XXH64_rotl(state->v2, 7) +
              XXH64_rotl(state->v3, 12) + XXH64_rotl(state->v4, 18);
        h64 = (h64 ^ XXH64_rotl(state->v1 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) *
              XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v2 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) *
              XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v3 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) *
              XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v4 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) *
              XXH_PRIME64_1 + XXH_PRIME64_4;
    } else {
        h64 = state->v3 + XXH_PRIME64_5;
    }
    h64 += state->total_len;

    unsigned char *p = state->mem;
    while (p + 8 <= state->mem + state->memsize) {
        unsigned long long k1;
        memcpy(&k1, p, 8);
        k1 *= XXH_PRIME64_2; k1 = XXH64_rotl(k1, 31); k1 *= XXH_PRIME64_1;
        h64 ^= k1;
        h64 = XXH64_rotl(h64, 27) * XXH_PRIME64_1 + XXH_PRIME64_4;
        p += 8;
    }
    if (p + 4 <= state->mem + state->memsize) {
        unsigned int k1;
        memcpy(&k1, p, 4);
        h64 ^= (unsigned long long)k1 * XXH_PRIME64_1;
        h64 = XXH64_rotl(h64, 23) * XXH_PRIME64_2 + XXH_PRIME64_3;
        p += 4;
    }
    while (p < state->mem + state->memsize) {
        h64 ^= (*p) * XXH_PRIME64_5;
        h64 = XXH64_rotl(h64, 11) * XXH_PRIME64_1;
        p++;
    }

    h64 ^= h64 >> 33;
    h64 *= XXH_PRIME64_2;
    h64 ^= h64 >> 29;
    h64 *= XXH_PRIME64_3;
    h64 ^= h64 >> 32;
    return h64;
}