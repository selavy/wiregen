#pragma once

#include <stdint.h>
#include <byteswap.h>
#include <string.h>

__attribute__((always_inline)) inline
void inplace_bswap_48(uint8_t val[6]) {
    uint64_t buffer;
    memcpy(&buffer, &val[0], 6);
    buffer = bswap_64(buffer);
    memcpy(&val[0], ((const uint8_t *)&buffer) + 2, 6);
}

__attribute__((always_inline)) inline
void inplace_bswap_56(uint8_t val[7]) {
    uint64_t buffer;
    memcpy(&buffer, &val[0], 7);
    buffer = bswap_64(buffer);
    memcpy(&val[0], ((const uint8_t *)&buffer) + 1, 7);
}

