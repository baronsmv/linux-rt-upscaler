/**
 * @file xxhash64.h
 * @brief Public domain xxHash64 implementation (embedded).
 *
 * Provides a fast, non-cryptographic hash for tile change detection.
 */

#ifndef XXHASH64_H
#define XXHASH64_H

#include <stddef.h>
#include <stdint.h>

typedef struct XXH64_state {
  unsigned long long total_len;
  unsigned long long v1, v2, v3, v4;
  unsigned char mem[32];
  unsigned memsize;
} XXH64_state_t;

void XXH64_reset(XXH64_state_t *state, unsigned long long seed);
void XXH64_update(XXH64_state_t *state, const void *input, size_t len);
unsigned long long XXH64_digest(XXH64_state_t *state);

#endif /* XXHASH64_H */