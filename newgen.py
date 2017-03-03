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
            ])

Struct = namedtuple(
        'Struct', [
            'display_name',
            'members'
            ])

def generate_struct_member(member):
    yield 'test'


if __name__ == '__main__':
    members = [
            StructMember(
                display_name='testr',
                bit_width=8,
                span=1,
                signed=True,
                little_endian=True,
                byte_aligned=True)
            ]

    for member in members:
        for line in generate_struct_member(member):
            print(line)
        print()

