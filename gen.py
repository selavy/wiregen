#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple
import math

# Types
EnumMember = namedtuple('EnumMember', ['name', 'value'])
Enum = namedtuple('Enum', ['name', 'members', 'width'])
StructMember = namedtuple('StructMember',
        ['name', 'btype', 'span', 'bigendian'])
Struct = namedtuple('Struct',
        ['name', 'width', 'span', 'members'])
Type = namedtuple('Type', ['width', 'ctype', 'span'])


# Globals
TYPES = {} # str -> Type
SWAPPERS = {} # str -> str, if not in map then don't need to swap


# Functions
def generate_enum(enum):
    yield 'enum {name} {{'.format(name=enum.name)
    align = 0
    for m in enum.members:
        align = max(len(m.name), align)
    for m in enum.members:
        yield '    {name:{align}} = {value},'.format(
                name=m.name, align=align, value=m.value)
    yield '};'
    rbytes = int(math.ceil(enum.width//8))
    yield '_Static_assert(sizeof(enum {name}) >= {rbytes},'.format(
            name=enum.name, rbytes=rbytes)
    yield '        "Not enough bits to encode enum {name}");'.format(
            name=enum.name)


def generate_bswapper(struct):
    yield '__attribute__((always_inline)) inline'
    yield 'void bswap_{name}(struct {name} *restrict val) {{'.format(
            name=struct.name)
    for m in struct.members:
        try:
            swapper = SWAPPERS[m.btype]
        except KeyError:
            continue
        # HACK(plesslie): probably should make this a tuple with
        # Boolean for inplace or not
        inplace = 'inplace' in swapper
        if inplace:
            yield '    {swapper}(val->{member});'.format(
                    swapper=swapper, member=m.name)
        else:
            yield '    val->{member} = {swapper}(val->{member});'.format(
                    swapper=swapper, member=m.name)
    yield '}'


def generate_struct_member(m):
    btype = TYPES[m.btype]
    span = btype.span * m.span
    if span > 1:
        spanstr = '[{span}]'.format(span=span)
    else:
        spanstr = ''
    yield '    {typename} {name}{span};'.format(
            typename=btype.ctype, name=m.name, span=spanstr)


def generate_struct(struct):
    yield 'struct {name} {{'.format(name=struct.name)
    for m in struct.members:
        for line in generate_struct_member(m):
            yield line
    yield '};'
    rbytes = int(math.ceil(struct.width//8))
    yield '_Static_assert(sizeof(struct {name}) == {width},'.format(
            name=struct.name, width=rbytes)
    yield '        "Incorrect size for struct {name}");'.format(
            name=struct.name)
    yield ''
    for line in generate_bswapper(struct):
        yield line


if __name__ == '__main__':
    # Basic Types
    TYPES['u8']  = Type(width=8 , ctype='uint8_t' , span=1)
    TYPES['u16'] = Type(width=16, ctype='uint16_t', span=1)
    TYPES['u32'] = Type(width=32, ctype='uint32_t', span=1)
    TYPES['u64'] = Type(width=64, ctype='uint64_t', span=1)

    TYPES['s8']  = Type(width=8 , ctype='uint8_t' , span=1)
    TYPES['s16'] = Type(width=16, ctype='uint16_t', span=1)
    TYPES['s32'] = Type(width=32, ctype='uint32_t', span=1)
    TYPES['s64'] = Type(width=64, ctype='uint64_t', span=1)

    TYPES['u48']  = Type(width=48 , ctype='uint8_t' , span=6)

    # Swappers for basic types
    SWAPPERS['u16'] = 'bswap_16'
    SWAPPERS['u32'] = 'bswap_32'
    SWAPPERS['u64'] = 'bswap_64'

    SWAPPERS['s16'] = 'bswap_16'
    SWAPPERS['s32'] = 'bswap_32'
    SWAPPERS['s64'] = 'bswap_64'

    SWAPPERS['u48'] = 'inplace_bswap_48'

    emembers = [
            EnumMember('ITCH5X_MT_SYSTEM_EVENT'            , "'S'"),
            EnumMember('ITCH5X_MT_STOCK_DIRECTORY'         , "'R'"),
            EnumMember('ITCH5X_MT_STOCK_TRADING_ACTION'    , "'H'"),
            EnumMember('ITCH5X_MT_REG_SHO_RESTRICTED_IND'  , "'Y'"),
            EnumMember('ITCH5X_MT_MKT_PARTICIPANT_POSITION', "'L'"),
            EnumMember('ITCH5X_MT_MWCB_DECLINE_LEVEL'      , "'V'"),
            EnumMember('ITCH5X_MT_MWCB_STATUS'             , "'W'"),
            EnumMember('ITCH5X_MT_IPO_QUOTING_UPDATE'      , "'K'"),
            EnumMember('ITCH5X_MT_ADD_ORDER'               , "'A'"),
            EnumMember('ITCH5X_MT_ADD_ORDER_ATTRIB'        , "'F'"),
            EnumMember('ITCH5X_MT_ORDER_EXECUTED'          , "'E'"),
            EnumMember('ITCH5X_MT_ORDER_EXECUTED_PRICE'    , "'C'"),
            EnumMember('ITCH5X_MT_ORDER_CANCEL'            , "'X'"),
            EnumMember('ITCH5X_MT_ORDER_DELETE'            , "'D'"),
            EnumMember('ITCH5X_MT_ORDER_REPLACE'           , "'U'"),
            EnumMember('ITCH5X_MT_TRADE'                   , "'P'"),
            EnumMember('ITCH5X_MT_CROSS_TRADE'             , "'Q'"),
            EnumMember('ITCH5X_MT_BROKEN_TRADE'            , "'B'"),
            EnumMember('ITCH5X_MT_NOII'                    , "'I'"),
            EnumMember('ITCH5X_MT_RPII'                    , "'N'"),
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


    smembers = [
            StructMember(name='message_type'          , btype='u8' , span=1, bigendian=True),
            StructMember(name='stock_locate'          , btype='u8' , span=1, bigendian=True),
            StructMember(name='tracking_number'       , btype='u16', span=1, bigendian=True),
            StructMember(name='tracking_number'       , btype='u48', span=1, bigendian=True),
            StructMember(name='order_reference_number', btype='u64', span=1, bigendian=True),
            StructMember(name='side'                  , btype='u8' , span=1, bigendian=True),
            StructMember(name='shares'                , btype='u32', span=1, bigendian=True),
            StructMember(name='stock'                 , btype='u8' , span=8, bigendian=True),
            StructMember(name='price'                 , btype='u32', span=1, bigendian=True),
            ]
    struct = Struct(name='itch5x_add_order',
            width=36*8,
            span=1,
            members=smembers)

    for line in generate_struct(struct):
        print(line)
    print()

