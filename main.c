#include "output.h"
#include <assert.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    uint8_t  message_type = ITCH5X_MT_ADD_ORDER;
    uint16_t stock_locate = 4575u;
    uint16_t tracking_number = 1345u;
    uint8_t  timestamp[6] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE };
    uint8_t  betimestamp[6] = { 0xFE, 0xCA, 0xEF, 0xBE, 0xAD, 0xDE };
    uint64_t order_reference_number = 0xDEADBEEFCAFEBABEull;
    uint8_t  side = 'B';
    uint32_t shares = 567u;
    uint8_t  stock[8] = { 'A', 'A', 'P', 'L', ' ', ' ', ' ', ' ' };
    uint32_t price = 98740100u;

    struct itch5x_add_order add;
    add.message_type = message_type;
    add.stock_locate = bswap_16(stock_locate);
    add.tracking_number = bswap_16(tracking_number);
    memcpy(&add.timestamp[0], &betimestamp[0], sizeof(add.timestamp));
    add.order_reference_number = bswap_64(order_reference_number);
    add.side = side;
    add.shares = bswap_32(shares);
    memcpy(&add.stock[0], &stock[0], sizeof(add.stock));
    add.price = bswap_32(price);

    bswap_itch5x_add_order(&add);

    assert(add.message_type == message_type);
    assert(add.stock_locate == stock_locate);
    assert(add.tracking_number = tracking_number);
    assert(memcmp(&add.timestamp[0], &timestamp[0], sizeof(add.timestamp)) == 0);
    assert(add.order_reference_number == order_reference_number);
    assert(add.side == side);
    assert(add.shares == shares);
    assert(memcmp(&add.stock[0], &stock[0], sizeof(stock)) == 0);
    assert(add.price == price);

    return 0;
}
