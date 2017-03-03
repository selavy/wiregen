#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple

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
            'members'
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
    for member in struct.members:
        for line in generate_struct_member(member):
            yield line


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
            StructMember(
                display_name='testrstructer',
                bit_width=64,
                span=6,
                signed=False,
                little_endian=True,
                byte_aligned=True,
                compound_type='test_t'),
            ]
    struct = Struct(display_name='HelloWorld', members=members)

    for line in generate_struct(struct):
        print(line)
    print()

#    for member in members:
#        for line in generate_struct_member(member):
#            print(line)
#    print()
