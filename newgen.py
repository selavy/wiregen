#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple
import math

StructMember = namedtuple(
        'StructMember', [
            'display_name',
            'bit_width',
            'span',
            'signed',
            'little_endian',
            'byte_aligned',
            'compound_type' # maybe None
            ])

Struct = namedtuple(
        'Struct', [
            'display_name',
            'members',
            ])

EnumMember = namedtuple(
        'EnumMember', [
            'display_name',
            'value',
            ])

Enum = namedtuple(
        'Enum', [
            'display_name',
            'members',
            'bit_width',
            ])


def generate_struct_member(member):
    if member.compound_type:
        ctype = 'struct {name}'.format(name=member.compound_type)
    else:
        if member.bit_width % 8 == 0 and member.bit_width >= 8:
            if member.bit_width > 64:
                raise ValueError('Unable to generate code for members greater than 64 bits wide')
            if member.signed:
                ctype = 'int{width}_t'.format(width=member.bit_width)
            else:
                ctype = 'uint{width}_t'.format(width=member.bit_width)

    if member.span > 1:
        span = '[{span}]'.format(span=member.span)
    else:
        span = ''

    yield '    {ctype} {display}{span};'.format(
            ctype=ctype, display=member.display_name, span=span)


def generate_struct(struct):
    yield 'struct {name} {{'.format(name=struct.display_name)
    width = 0
    for member in struct.members:
        for line in generate_struct_member(member):
            yield line
        width += member.bit_width * member.span
    yield '} __attribute__((packed));'
    if width % 8 == 0:
        yield '_Static_assert(sizeof(struct {name}) == {width}, "Width of {name} incorrect");'.format(
                name=struct.display_name, width=width//8)


def generate_enum_member(member):
    if isinstance(member.value, str):
        if len(member.value) != 1:
            raise ValueError('Enum values must be single character or int!')
        yield "    {name} = '{value}',".format(
                name=member.display_name, value=member.value)
    else:
        yield '    {name} = {value},'.format(
                name=member.display_name, value=member.value)


def required_bits(value):
    if isinstance(value, str):
        value = ord(value)
    if not isinstance(value, int):
        raise ValueError("Value must be int or char")
    return int(math.ceil(math.log(value, 2)))


def next_power_of_two(x):
    return 1 << (x-1).bit_length()


def generate_enum(enum):
    yield 'enum {name} {{'.format(name=enum.display_name)
    bits = 0
    for member in enum.members:
        for line in generate_enum_member(member):
            yield line
        rbits = required_bits(member.value)
        if rbits > bits:
            bits = rbits
    yield '};'
    if bits > enum.bit_width:
        raise Exception("Not enough bits to encode enum {name}".format(
            name=enum.display_name))
    #bits = next_power_of_two(bits)
    #assert bits % 8 == 0
    #byts = bits / 8
    #yield '_Static_assert(sizeof(enum {name}) == {byts}, "Width of {name} incorrect");'.format(
    #        name=enum.display_name, byts=byts)


if __name__ == '__main__':
    members = [
            StructMember(
                display_name='testr',
                bit_width=8,
                span=1,
                signed=True,
                little_endian=True,
                byte_aligned=True,
                compound_type=None),
            StructMember(
                display_name='testr_unsigned',
                bit_width=8,
                span=1,
                signed=False,
                little_endian=True,
                byte_aligned=True,
                compound_type=None),
            StructMember(
                display_name='arr',
                bit_width=64,
                span=6,
                signed=False,
                little_endian=True,
                byte_aligned=True,
                compound_type=None),
            ]
    struct = Struct(display_name='HelloWorld', members=members)


    emembers = [
        EnumMember(display_name='ITCH5x_MT_SYSTEM_EVENT_MESSAGE', value='S'),
        EnumMember(display_name='ITCH5x_MT_STOCK_DIRECTORY', value='R'),
        EnumMember(display_name='ITCH5x_MT_STOCK_TRADING_ACTION', value='H'),
        EnumMember(display_name='ITCH5x_MT_REG_SHO_INDICATOR', value='Y'),
        EnumMember(display_name='ITCH5x_MT_MKT_PARTICIPANT_POSITION', value='L'),
        EnumMember(display_name='ITCH5x_MT_MWCB_LEVEL_DECLINE', value='V'),
        EnumMember(display_name='ITCH5x_MT_MWCB_STATUS', value='W'),
        EnumMember(display_name='ITCH5x_MT_IPO_QUOTING_PERIOD_UPDATE', value='K'),
        EnumMember(display_name='ITCH5x_MT_ADD_ORDER', value='A'),
        EnumMember(display_name='ITCH5x_MT_ADD_ORDER_ATTRIBUTED', value='F'),
        EnumMember(display_name='ITCH5x_MT_ORDER_EXECUTED', value='E'),
        EnumMember(display_name='ITCH5x_MT_ORDER_EXECUTED_WITH_PRICE', value='C'),
        EnumMember(display_name='ITCH5x_MT_ORDER_CANCEL', value='X'),
        EnumMember(display_name='ITCH5x_MT_ORDER_DELETE', value='D'),
        EnumMember(display_name='ITCH5x_MT_ORDER_REPLACE', value='U'),
        EnumMember(display_name='ITCH5x_MT_TRADE', value='P'),
        EnumMember(display_name='ITCH5x_MT_CROSS_TRADE', value='Q'),
        EnumMember(display_name='ITCH5x_MT_BROKEN_TRADE', value='B'),
        EnumMember(display_name='ITCH5x_MT_NOII', value='I'),
        EnumMember(display_name='ITCH5x_MT_RPII', value='N'),
    ]
    enum = Enum(display_name='itch5x_msg_type', members=emembers, bit_width=8)

    print('#pragma once')
    print()
    print('#include <stdint.h>')
    print()
    print('/* Generate file.  Do not edit by hand */')
    print()

    for line in generate_struct(struct):
        print(line)
    print()

    for line in generate_enum(enum):
        print(line)
    print()

#    for member in members:
#        for line in generate_struct_member(member):
#            print(line)
#    print()
