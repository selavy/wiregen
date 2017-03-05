#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple
import math
import re
import sys

# Future support ideas:
#   +namespace "itch5x", prepends "itch5x_" to every type
#   +compound types within other compound types
#   +debug pretty printer?
#   +bitfields
#   +string field accessors (null vs space padded)

# Types
EnumMember = namedtuple('EnumMember', ['name', 'value'])
Enum = namedtuple('Enum', ['name', 'members', 'width'])
StructMember = namedtuple('StructMember',
        ['name', 'btype', 'span'])
Struct = namedtuple('Struct',
        ['name', 'width', 'span', 'members'])
Type = namedtuple('Type', ['width', 'ctype', 'span'])

class TokenType(object):
    UNK = 0
    KWENUM = 1
    KWSTRUCT = 2
    IDENT = 3
    EQUALS = 4
    LBRACE = 5
    RBRACE = 6
    COMMA = 7
    CHARACTER = 8
    SEMICOLON = 9
    LSBRACKET = 10
    RSBRACKET = 11
    INTEGER = 12
    LPAREN = 13
    RPAREN = 14
    EOF = 15

Token = namedtuple('Token', ['ttype', 'value', 'linum', 'col'])

class Lexer(object):
    _rules = [
            (r'\d+'          , TokenType.INTEGER),
            (r'\('           , TokenType.LPAREN),
            (r'\)'           , TokenType.RPAREN),
            (r'='            , TokenType.EQUALS),
            (r','            , TokenType.COMMA),
            (r"'[a-zA-Z0-9]'", TokenType.CHARACTER),
            (r';'            , TokenType.SEMICOLON),
            (r'\['           , TokenType.LSBRACKET),
            (r'\]'           , TokenType.RSBRACKET),
            (r'\{'            , TokenType.LBRACE),
            (r'\}'            , TokenType.RBRACE),
            (r'enum'         , TokenType.KWENUM),
            (r'struct'       , TokenType.KWSTRUCT),
            (r'[a-zA-Z_][a-zA-Z0-9_]*' , TokenType.IDENT),
            ]

    def __init__(self, lines):
        self.linum = 1
        self.lines = lines
        self.line = next(self.lines)
        self.pos = 0
        self.rules = []
        for regex, ttype in Lexer._rules:
            self.rules.append((re.compile(regex), ttype))
        self._ws_skip = re.compile('\S')

    def _adv_line(self):
        self.pos = 0
        self.linum += 1
        self.line = next(self.lines)

    def tokenize(self):
        while 1:
            while 1:
                m = self._ws_skip.search(self.line, self.pos)
                if m:
                    self.pos = m.start()
                    break
                else:
                    self._adv_line()

            matched = False
            for regex, ttype in self.rules:
                m = regex.match(self.line, self.pos)
                if m:
                    tok = Token(ttype=ttype, value=m.group(),
                            linum=self.linum, col=self.pos)
                    self.pos = m.end()
                    yield tok
                    matched = True

            if not matched:
                raise Exception('LexerError({line}, {col}): bad value'.format(
                    line=self.linum, col=self.pos))

            if self.pos > len(self.line):
                self._adv_line()
        print("Fell out of while loop")


# TODO(plesslie): this naming (Tokenizer and Lexer) is confusing - really
# should just put it all into Lexer
class Tokenizer(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = self.lexer.tokenize()
        self.cur = next(self.tokens)

    def _next(self):
        try:
            self.cur = next(self.tokens)
        except StopIterator:
            self.cur = Token(ttype=TokenType.EOF, value='', linum=None, col=None)

    def peek(self):
        return self.cur

    def expect(self, ttype):
        if self.cur.ttype != ttype:
            raise Exception('Error ({line}, {col}): Expected token of type {e}, instead found token of type {a}'.format(
                line=self.cur.linum, col=self.cur.col, e=ttype, a=self.cur.ttype))
        self._next()

    def accept(self, ttype):
        if self.cur.ttype == ttype:
            self._next()
            return True
        else:
            return False

    def linum(self):
        return self.cur.linum

    def column(self):
        return self.cur.col


def parse(tokens):
    while not tokens.accept(TokenType.EOF):
        if tokens.accept(TokenType.KWSTRUCT):
            yield parse_struct(tokens)
        elif tokens.accept(TokenType.KWENUM):
            print("calling parse_enum")
            for line in parse_enum(tokens):
                yield line
        else:
            raise Exception("ParseError({line}, {col}): Unexpected token '{tok}'".format(
                line=tokens.linum(), col=tokens.column(), tok=tokens.peek().value))

def parse_enum(tokens):
    name = tokens.peek().value
    tokens.expect(TokenType.IDENT)
    tokens.expect(TokenType.LBRACE)
    values = parse_enum_members(tokens)
    width = 0
    for v in values:
        if isinstance(v.value, str):
            value = ord(v.value[1])
        else:
            value = v.value
        bits = value.bit_length()
        width = max(width, bits)
    while width % 8 != 0:
        width += 1
    enum = Enum(name=name, members=values, width=width)
    for line in generate_enum(enum):
        yield line
    raise StopIteration


def parse_enum_members(tokens):
    members = []
    while not tokens.accept(TokenType.RBRACE):
        name = tokens.peek().value
        tokens.expect(TokenType.IDENT)
        tokens.expect(TokenType.EQUALS)
        value = tokens.peek().value
        if not (tokens.accept(TokenType.CHARACTER) or tokens.accept(TokenType.INTEGER)):
            raise Exception('ParseError({line}, {col}): Expected character or integer for enum value'.format(
                line=tokens.linum(), col=tokens.column()))
        members.append(EnumMember(name=name, value=value))
        if not tokens.accept(TokenType.COMMA):
            break
    return members


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
    yield '} __attribute__((packed));'
    rbytes = int(math.ceil(struct.width//8))
    yield '_Static_assert(sizeof(struct {name}) == {width},'.format(
            name=struct.name, width=rbytes)
    yield '        "Incorrect size for struct {name}");'.format(
            name=struct.name)
    yield ''
    for line in generate_bswapper(struct):
        yield line


if __name__ == '__main__':
    with open('itch5x.idl') as f:
        lexer = Lexer(lines=f)
        tokens = Tokenizer(lexer)
        for line in parse(tokens):
            print(line)
    sys.exit()

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
    print('#include "bswap_util.h"')
    print()
    #print('// Generated file.  Do not edit.')
    print("/* Do not edit.  Generated by 'wiregen.py itch5x.idl' */")

    print()

    for line in generate_enum(enum):
        print(line)
    print()


    smembers = [
            StructMember(name='message_type'          , btype='u8' , span=1),
            StructMember(name='stock_locate'          , btype='u16', span=1),
            StructMember(name='tracking_number'       , btype='u16', span=1),
            StructMember(name='timestamp'             , btype='u48', span=1),
            StructMember(name='order_reference_number', btype='u64', span=1),
            StructMember(name='side'                  , btype='u8' , span=1),
            StructMember(name='shares'                , btype='u32', span=1),
            StructMember(name='stock'                 , btype='u8' , span=8),
            StructMember(name='price'                 , btype='u32', span=1),
            ]
    struct = Struct(name='itch5x_add_order',
            width=36*8,
            span=1,
            members=smembers)

    for line in generate_struct(struct):
        print(line)
    print()

