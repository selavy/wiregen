#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple
import math

EnumMember = namedtuple('EnumMember', ['name', 'value'])
Enum = namedtuple('Enum', ['name', 'members', 'width'])
StructMember = namedtuple('StructMember',
        ['name', 'width', 'span', 'bigendian'])
Struct = namedtuple('Struct', ['name', 'width', 'span', 'bigendian'])


def generate_enum(enum):
    yield 'enum {name} {{'.format(name=enum.name)
    yield '};'
    rbytes = int(math.ceil(enum.width//8))
    yield '_Static_assert(sizeof(enum {name}) >= {rbytes},'.format(
            name=enum.name, rbytes=rbytes)
    yield '        "Not enough bits to encode enum {name}");'.format(
            name=enum.name)



if __name__ == '__main__':
    emembers = [
            EnumMember('ITCH5X_MT_SYSTEM_EVENT'            , 'S'),
            EnumMember('ITCH5X_MT_STOCK_DIRECTORY'         , 'R'),
            EnumMember('ITCH5X_MT_STOCK_TRADING_ACTION'    , 'H'),
            EnumMember('ITCH5X_MT_REG_SHO_RESTRICTED_IND'  , 'Y'),
            EnumMember('ITCH5X_MT_MKT_PARTICIPANT_POSITION', 'L'),
            EnumMember('ITCH5X_MT_MWCB_DECLINE_LEVEL'      , 'V'),
            EnumMember('ITCH5X_MT_MWCB_STATUS'             , 'W'),
            EnumMember('ITCH5X_MT_IPO_QUOTING_UPDATE'      , 'K'),
            EnumMember('ITCH5X_MT_ADD_ORDER'               , 'A'),
            EnumMember('ITCH5X_MT_ADD_ORDER_ATTRIB'        , 'F'),
            EnumMember('ITCH5X_MT_ORDER_EXECUTED'          , 'E'),
            EnumMember('ITCH5X_MT_ORDER_EXECUTED_PRICE'    , 'C'),
            EnumMember('ITCH5X_MT_ORDER_CANCEL'            , 'X'),
            EnumMember('ITCH5X_MT_ORDER_DELETE'            , 'D'),
            EnumMember('ITCH5X_MT_ORDER_REPLACE'           , 'U'),
            EnumMember('ITCH5X_MT_TRADE'                   , 'P'),
            EnumMember('ITCH5X_MT_CROSS_TRADE'             , 'Q'),
            EnumMember('ITCH5X_MT_BROKEN_TRADE'            , 'B'),
            EnumMember('ITCH5X_MT_NOII'                    , 'I'),
            EnumMember('ITCH5X_MT_RPII'                    , 'N'),
            ]
    enum = Enum(name='itch5x_message_type', members=emembers, width=8)


    print('#pragma once')
    print()
    print('#include "bswap_util.h')
    print()
    print('// Generated file.  Do not edit.')
    print()

    for line in generate_enum(enum):
        print(line)
    print()
