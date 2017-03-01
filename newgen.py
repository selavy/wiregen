#!/usr/bin/env python

from __future__ import print_function
import sys
import pprint
import math

def required_bits(value):
    return math.ceil(math.log(value, 2))


def next_power_of_two(value):
    return 1 << (x-1).bit_length()


class EnumValue(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return '{name} = {value}'.format(name=self.name, value=self.value)

    def __repr__(self):
        return self.__str__()


class Enum(object):
    def __init__(self, name, members, attribs):
        self.name = name
        self.members = members
        self.attribs = attribs

        width = 0
        for m in members:
            value = m.value
            if isinstance(value, str):
                if len(value) != 3:
                    raise Exception("Invalid enum value: {}".format(value))
                value = ord(value[1])
            elif not isinstance(value, int):
                raise Exception("Invalid enum value: {}".format(value))
            w = required_bits(value)
            if w > width:
                width = w
            if 'bits' in attribs:
                bits = attribs['bits']
                if width > bits:
                    raise Exception('Enum {} requires {} bits, but specified width is {} bits'.format(
                        self.name, width, bits))
                self.width = bits
                self.aligned = bits % 8 == 0
            elif 'bytes' in attribs:
                bytes_ = attribs['bytes']
                reqbytes = width / 8.
                if reqbytes > bytes_:
                    raise Exception('Enum {} requires {} bytes, but specified width is {} bytes'.format(
                        self.name, reqbytes, bytes_))
                self.width = bytes_ * 8
                self.aligned = True
            else:
                self.width = next_power_of_two(width)
                self.aligned = True


class Struct(object):
    def __init__(self, name, members, attribs):
        self.name = name
        self.members = members
        self.attribs = attribs

    def __str__(self):
        return 'Struct({})'.format(self.name)

    def __repr__(self):
        return self.__str__()


class BasicType(object):
    def __init__(self, name, width, signed):
        self.name = name
        self.width = width
        self.signed = signed


class StructMember(object):
    def __init__(self, name, type_, span, attribs):
        self.name = name
        self.type_ = type_
        if span < 1:
            raise ValueError("Span of type must be greater than or equal to 1, instead received {}".format(
                span))
        self.span = span
        self.attribs = attribs


class TokenType(object):
    COMMA = 0
    SEMICOLON = 1
    LPAREN = 2
    RPAREN = 3
    LBRACKET = 4
    RBRACKET = 5
    LBRACE = 6
    RBRACE = 7
    INTEGER = 8
    IDENT = 9
    STRING = 10
    KWENUM = 11
    KWSTRUCT = 12
    COLON = 13
    EQUALS = 14
    UNK = 15
    WHITESPACE = 16
    CHARACTER = 17 # character surrounded by single quote
    EOF = 18

    @staticmethod
    def tostr(t):
        if t == TokenType.COMMA:
            return ','
        elif t == TokenType.SEMICOLON:
            return ';'
        elif t == TokenType.LPAREN:
            return '('
        elif t == TokenType.RPAREN:
            return ')'
        elif t == TokenType.LBRACKET:
            return '['
        elif t == TokenType.RBRACKET:
            return ']'
        elif t == TokenType.LBRACE:
            return '{'
        elif t == TokenType.RBRACE:
            return '}'
        elif t == TokenType.INTEGER:
            return 'integer'
        elif t == TokenType.IDENT:
            return 'ident'
        elif t == TokenType.STRING:
            return 'string'
        elif t == TokenType.KWENUM:
            return 'enum'
        elif t == TokenType.COLON:
            return ':'
        elif t == TokenType.EQUALS:
            return '='
        elif t == TokenType.WHITESPACE:
            return 'whitespace'
        elif t == TokenType.CHARACTER:
            return "character"
        elif t == TokenType.EOF:
            return 'EOF'
        elif t == TokenType.KWSTRUCT:
            return 'struct'
        else:
            raise Exception('Unknown type: {}'.format(t))

class Token(object):
    def __init__(self, type_, value, linum):
        self.type_ = type_
        self.value = value
        self.linum = linum

    def __str__(self):
        return 'Token({typ}) = "{val}"'.format(
                typ=TokenType.tostr(self.type_), val=self.value)


def _tokenize(stream):
    size = len(stream)
    i = 0
    linum = 1
    while 1:
        while i < size and stream[i].isspace():
            if stream[i] == '\n':
                linum += 1
            i += 1
        if not (i < size):
            break
        c = stream[i]
        i += 1
        if c == '(':
            yield Token(TokenType.LPAREN, '(', linum)
        elif c == ')':
            yield Token(TokenType.RPAREN, ')', linum)
        elif c == '[':
            yield Token(TokenType.LBRACKET, '[', linum)
        elif c == ']':
            yield Token(TokenType.RBRACKET, ']', linum)
        elif c == '{':
            yield Token(TokenType.LBRACE, '{', linum)
        elif c == '}':
            yield Token(TokenType.RBRACE, '}', linum)
        elif c == ':':
            yield Token(TokenType.COLON, ':', linum)
        elif c == ',':
            yield Token(TokenType.COMMA, ',', linum)
        elif c == '=':
            yield Token(TokenType.EQUALS, '=', linum)
        elif c == "'":
            val = ''
            while i < size and stream[i] != "'" and stream[i] != '\n':
                val += stream[i]
                i += 1
            if len(val) != 1 or stream[i] == '\n':
                raise Exception("Expected value between single quotes to be single character")
            i += 1
            yield Token(TokenType.CHARACTER, val, linum)
        elif c == ';':
            yield Token(TokenType.SEMICOLON, ';', linum)
        elif c == '"':
            val = c
            while i < size and stream[i] != '"' and stream[i] != '\n':
                val += stream[i]
                i += 1
            if i >= size or stream[i] == '\n':
                raise Exception('''Unmatched '"' character''')
            i += 1
            yield Token(TokenType.STRING, val, linum)
        elif c.isdigit():
            val = c
            while i < size and stream[i].isdigit():
                val += stream[i]
                i += 1
            yield Token(TokenType.INTEGER, val, linum)
        else:
            val = c
            while i < size:
                c = stream[i]
                if not (c.isalpha() or c.isdigit() or c == '_'):
                    break
                val += c
                i += 1
            if val == 'enum':
                yield Token(TokenType.KWENUM, val, linum)
            elif val == 'struct':
                yield Token(TokenType.KWSTRUCT, val, linum)
            else:
                yield Token(TokenType.IDENT, val, linum)


class Lexer(object):
    def __init__(self, lines):
        self.tokenizer = _tokenize(lines)
        self.cur = self.tokenizer.next()

    def next(self):
        try:
            self.cur = self.tokenizer.next()
        except StopIteration:
            self.cur = Token(TokenType.EOF, '', 0)
        return self.cur

    def peek(self):
        return self.cur

    def expect(self, type_):
        if self.cur.type_ != type_:
            raise Exception('SyntaxError({}): expected {} token, instead received {} = "{}"'.format(
                self.cur.linum,
                TokenType.tostr(type_),
                TokenType.tostr(self.cur.type_),
                self.cur.value))
        else:
            self.next()

    def accept(self, type_):
        if self.cur.type_ == type_:
            self.next()
            return True
        else:
            return False


def parse(lexer):
    enums = []
    structs = []
    while not lexer.accept(TokenType.EOF):
        if lexer.accept(TokenType.KWENUM):
            enum = parse_enum(lexer)
            enums.append(enum)
        elif lexer.accept(TokenType.KWSTRUCT):
            struct = parse_struct(lexer)
            pprint.pprint(struct)
            structs.append(struct)
        else:
            raise Exception('Unexpected token type {}'.format(
                TokenType.tostr(lexer.peek().type_)))
    return enums, structs

def parse_attributes(lexer):
    attribs = {}
    if lexer.accept(TokenType.LPAREN):
        while not lexer.accept(TokenType.RPAREN):
            key = lexer.peek().value
            lexer.expect(TokenType.IDENT)
            lexer.expect(TokenType.EQUALS)
            val = lexer.peek().value
            if lexer.accept(TokenType.INTEGER):
                val = int(val)
            elif lexer.accept(TokenType.CHARACTER):
                val = "'{}'".format(val)
            elif not lexer.accept(TokenType.STRING):
                raise Exception('Expected integer or string value in attributes list, instead received {} = "{}"'.format(
                    TokenType.tostr(lexer.peek().type_), lexer.peek().value))
            attribs[key] = val
            if lexer.accept(TokenType.COMMA):
                continue
    return attribs

def parse_struct(lexer):
    name = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    attribs = parse_attributes(lexer)
    lexer.expect(TokenType.LBRACE)
    members = [m for m in parse_struct_member(lexer)]
    return Struct(name=name, members=members, attribs=attribs)


def parse_struct_member(lexer):
    while not lexer.accept(TokenType.RBRACE):
        name = lexer.peek().value
        lexer.expect(TokenType.IDENT)
        lexer.expect(TokenType.COLON)
        type_ = lexer.peek().value
        lexer.expect(TokenType.IDENT)
        span = 1
        if lexer.accept(TokenType.LBRACKET):
            span = lexer.peek().value
            lexer.expect(TokenType.INTEGER)
            span = int(span)
            lexer.expect(TokenType.RBRACKET)
        attribs = parse_attributes(lexer)
        yield StructMember(name=name, type_=type_, span=span, attribs=attribs)
        if not lexer.accept(TokenType.SEMICOLON):
            break


def parse_enum(lexer):
    name = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    attribs = parse_attributes(lexer)
    print("Parsed attributes: {}".format(str(attribs)))
    lexer.expect(TokenType.LBRACE)
    members = [m for m in parse_enum_member(lexer)]
    if not members:
        raise Exception('Enum type "{}" has no members!'.format(name))
    return Enum(name=name, members=members, attribs=attribs)


def parse_enum_member(lexer):
    while not lexer.accept(TokenType.RBRACE):
        name = lexer.peek().value
        lexer.expect(TokenType.IDENT)
        lexer.expect(TokenType.EQUALS)
        val = lexer.peek().value
        if lexer.accept(TokenType.CHARACTER):
            value = "'{}'".format(val)
        elif lexer.accept(TokenType.INTEGER):
            value = int(val)
        else:
            raise Exception("Expected character or integer value for enum value")
        if not lexer.accept(TokenType.COMMA):
            break
        yield EnumValue(name=name, value=value)


def generate_enum(enum):
    yield 'enum {name} {{'.format(name=enum.name)
    for m in enum.members:
        yield '    {name} = {value},'.format(name=m.name, value=m.value)
    yield '};'
    yield '// size = {width}'.format(width=enum.width)
    yield '// aligned = {aligned}'.format(aligned=enum.aligned)
    if enum.aligned:
        yield 'static_assert(sizeof({name}) <= {width});'.format(
                name=enum.name, width=enum.width)


if __name__ == '__main__':
    with open('itch5x.idl') as f:
        lines = f.readlines()
    lines = '\n'.join(lines)
    lexer = Lexer(lines)
    enums, structs = parse(lexer)

    basics = {}
    basics['u8' ] = BasicType(name='u8' , width=8 , signed=False)
    basics['u16'] = BasicType(name='u16', width=16, signed=False)
    basics['u32'] = BasicType(name='u32', width=32, signed=False)
    basics['u64'] = BasicType(name='u64', width=64, signed=False)

    basics['s8' ] = BasicType(name='s8' , width=8 , signed=True)
    basics['s16'] = BasicType(name='s16', width=16, signed=True)
    basics['s32'] = BasicType(name='s32', width=32, signed=True)
    basics['s64'] = BasicType(name='s64', width=64, signed=True)

    for enum in enums:
        for line in generate_enum(enum):
            print(line)
        print()

#    for struct in structs:
#        for line in generate_struct(struct, enums=enums, basics=basics):
#            print(line)
#        print()
#
