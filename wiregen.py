#!/usr/bin/env python

from __future__ import print_function
import sys
from collections import namedtuple
import pprint


Token = namedtuple('Token', ['type', 'value', 'linum'])
Enum = namedtuple('Enum', ['name', 'width', 'members'])
EnumMember = namedtuple('EnumMember', ['name', 'value'])
Struct = namedtuple('Struct', ['name', 'bit_width', 'byte_width', 'members'])
StructMember = namedtuple('StructMember', ['name', 'typedecl'])
TypeDecl = namedtuple('TypeDecl', ['name', 'array_width'])
BasicType = namedtuple('BasicType', ['width', 'span', 'signed', 'ctype'])


class TokenType(object):
    KWENUM = 0
    KWSTRUCT = 1
    LBRACE = 2
    RBRACE = 3
    LPAREN = 4
    RPAREN = 5
    SEMICOLON = 6
    EQUALS = 7
    LBRACKET = 8
    RBRACKET = 9
    QUOTE = 10
    NUMBER = 11
    IDENT = 12
    COMMA = 13
    KWBITS = 14
    KWBYTES = 15
    KWTYPEDEF = 16
    EOF = 17

    @staticmethod
    def tostr(token):
        if token == TokenType.KWENUM:
            return 'enum'
        elif token == TokenType.KWSTRUCT:
            return 'struct'
        elif token == TokenType.LBRACE:
            return '{'
        elif token == TokenType.RBRACE:
            return '}'
        elif token == TokenType.LPAREN:
            return '('
        elif token == TokenType.RPAREN:
            return ')'
        elif token == TokenType.SEMICOLON:
            return ';'
        elif token == TokenType.EQUALS:
            return '='
        elif token == TokenType.LBRACKET:
            return '['
        elif token == TokenType.RBRACKET:
            return ']'
        elif token == TokenType.QUOTE:
            return "'"
        elif token == TokenType.NUMBER:
            return 'number'
        elif token == TokenType.IDENT:
            return 'identifier'
        elif token == TokenType.COMMA:
            return ','
        elif token == TokenType.KWBITS:
            return 'bits'
        elif token == TokenType.KWBYTES:
            return 'bytes'
        elif token == TokenType.KWTYPEDEF:
            return 'typedef'
        elif token == TokenType.EOF:
            return 'EOF'
        else:
            raise Exception('Unknown token type!')


def is_ident(token):
    if not token:
        return False
    if not token[0].isalpha():
        return False
    for c in token:
        if not (c.isalnum() or c == '_'):
            return False
    return True


def _tokenize(lines):
    for i, line in enumerate(lines):
        if not line or line[0] == '#':
            continue
        linum = i + 1

        # hack to make str.split() correctly split on token
        line = line.replace('(', ' ( ')
        line = line.replace(')', ' ) ')
        line = line.replace('{', ' { ')
        line = line.replace('}', ' } ')
        line = line.replace(';', ' ; ')
        line = line.replace('=', ' = ')
        line = line.replace('[', ' [ ')
        line = line.replace(']', ' ] ')
        line = line.replace("'", " ' ")
        line = line.replace(',', ' , ')
        for token in line.split():
            if token == 'enum':
                yield Token(type=TokenType.KWENUM, value=token, linum=linum)
            elif token == 'struct':
                yield Token(type=TokenType.KWSTRUCT, value=token, linum=linum)
            elif token == 'bits':
                yield Token(type=TokenType.KWBITS, value=token, linum=linum)
            elif token == 'bytes':
                yield Token(type=TokenType.KWBYTES, value=token, linum=linum)
            elif token == 'typedef':
                yield Token(type=TokenType.KWTYPEDEF, value=token, linum=linum)
            elif token == '(':
                yield Token(type=TokenType.LPAREN, value=token, linum=linum)
            elif token == ')':
                yield Token(type=TokenType.RPAREN, value=token, linum=linum)
            elif token == '{':
                yield Token(type=TokenType.LBRACE, value=token, linum=linum)
            elif token == '}':
                yield Token(type=TokenType.RBRACE, value=token, linum=linum)
            elif token == ';':
                yield Token(type=TokenType.SEMICOLON, value=token, linum=linum)
            elif token == '=':
                yield Token(type=TokenType.EQUALS, value=token, linum=linum)
            elif token == '[':
                yield Token(type=TokenType.LBRACKET, value=token, linum=linum)
            elif token == ']':
                yield Token(type=TokenType.RBRACKET, value=token, linum=linum)
            elif token == "'":
                yield Token(type=TokenType.QUOTE, value=token, linum=linum)
            elif token == ',':
                yield Token(type=TokenType.COMMA, value=token, linum=linum)
            elif token.isdigit():
                yield Token(type=TokenType.NUMBER, value=int(token), linum=linum)
            elif is_ident(token):
                yield Token(type=TokenType.IDENT, value=token, linum=linum)
            else:
                raise Exception("Syntax Error on line {}: '{}'".format(
                    linum, token))


class Tokenizer(object):

    def __init__(self, lines):
        self.tokens = _tokenize(lines)
        self.token = self.tokens.next()

    def peek(self):
        return self.token

    def next(self):
        try:
            self.token = self.tokens.next()
        except StopIteration:
            self.token = Token(type=TokenType.EOF, value='', linum=-1)
        return self.token

    def accept(self, type_):
        if self.token.type == type_:
            self.next()
            return True
        else:
            return False

    def expect(self, type_):
        if not self.accept(type_):
            raise Exception("SyntaxError({linum}): expected '{typ}' token, instead received '{tkn}'".format(
                linum=self.token.linum, typ=TokenType.tostr(type_), tkn=self.token.value))


def parse(lexer):
    enums = []
    structs = []
    typedefs = {} # alias -> original type

    while not lexer.accept(TokenType.EOF):
        if lexer.accept(TokenType.KWENUM):
            enum = parse_enum(lexer)
            enums.append(enum)
        elif lexer.accept(TokenType.KWSTRUCT):
            struct = parse_struct(lexer)
            structs.append(struct)
        elif lexer.accept(TokenType.KWTYPEDEF):
            alias, typedecl = parse_typedef(lexer)
            typedefs[alias] = typedecl
        else:
            token = lexer.peek()
            raise Exception("SyntaxError({}): Invalid token '{}'".format(
                token.linum, token.value))

    return enums, structs, typedefs


def parse_typedecl(lexer):
    array_width = 0
    name = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    if lexer.accept(TokenType.LBRACKET):
        array_width = lexer.peek().value
        lexer.expect(TokenType.NUMBER)
        lexer.expect(TokenType.RBRACKET)
    return TypeDecl(name=name, array_width=int(array_width))


def parse_typedef(lexer):
    # right now "typedefs" can only alias a typedecl to
    # a new name.
    typedecl = parse_typedecl(lexer)
    alias = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    lexer.expect(TokenType.SEMICOLON)
    return alias, typedecl


def parse_struct(lexer):
    bit_width = 0
    byte_width = 0
    if lexer.accept(TokenType.KWBITS):
        lexer.expect(TokenType.RPAREN)
        bit_width = lexer.peek().value
        lexer.expect(TokenType.NUMBER)
        lexer.expect(TokenType.RPAREN)
    elif lexer.accept(TokenType.KWBYTES):
        lexer.expect(TokenType.RPAREN)
        byte_width = lexer.peek().value
        lexer.expect(TokenType.NUMBER)
        lexer.expect(TokenType.RPAREN)

    name = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    lexer.expect(TokenType.LBRACE)

    members = [x for x in parse_struct_member(lexer)]
    if not members:
        raise Exception("Struct '{}' declared with no members!".format(
            name))

    lexer.expect(TokenType.RBRACE)
    return Struct(name=name, bit_width=bit_width, byte_width=byte_width,
            members=members)


def parse_struct_member(lexer):
    """
    Member grammar:
    member_list ::= member member_list
                  | member
                  ;
    member      ::= type_decl member_name ';';
    member_name ::= IDENT;
    type_decl   ::= IDENT '[' NUMBER ']'
                  | IDENT
                  ;
    """

    while lexer.peek().type != TokenType.RBRACE:
        #array_width = 0
        typedecl = parse_typedecl(lexer)
#        type_ = lexer.peek().value
#        lexer.expect(TokenType.IDENT)
#        if lexer.accept(TokenType.LBRACKET):
#            array_width = lexer.peek().value
#            lexer.expect(TokenType.NUMBER)
#            lexer.expect(TokenType.RBRACKET)
        name = lexer.peek().value
        lexer.expect(TokenType.IDENT)
        lexer.expect(TokenType.SEMICOLON)
        yield StructMember(name=name, typedecl=typedecl)


def parse_enum(lexer):
    """
    Enum grammar:
    enum        ::= 'enum' width_decl '{' member_list '}'
    width_decl  ::= 'bits' '(' NUMBER ')'
                  | 'bytes' '(' NUMBER ')'
                  | [empty]
                  ;
    """
    if lexer.accept(TokenType.KWBITS):
        lexer.expect(TokenType.LPAREN)
        token = lexer.peek()
        lexer.expect(TokenType.NUMBER)
        width = token.value
        lexer.expect(TokenType.RPAREN)

    name = lexer.peek().value
    lexer.expect(TokenType.IDENT)
    lexer.expect(TokenType.LBRACE)

    members = [x for x in parse_enum_member(lexer)]
    if not members:
        raise Exception("Enum '{}' declared with no values!".format(
            name))

    lexer.expect(TokenType.RBRACE)
    return Enum(name=name, width=width, members=members)


def parse_enum_member(lexer):
    """
    Enum member grammar:
    # basically this, but last comma not required
    member_list ::= member_decl member_list
                  | member_decl,
                  ;
    member_decl ::= IDENT = "'" value "'"
    """
    while lexer.peek().type != TokenType.RBRACE:
        token  = lexer.peek()
        name = token.value
        lexer.expect(TokenType.IDENT)
        lexer.expect(TokenType.EQUALS)

        token = lexer.peek()
        if lexer.accept(TokenType.NUMBER):
            value = token.value
        elif lexer.accept(TokenType.QUOTE):
            token = lexer.peek()
            lexer.expect(TokenType.IDENT)
            if len(token.value) != 1 or not token.value.isalpha():
                raise Exception("Invalid enum value: '{}'".format(token.value))
            value = "'{val}'".format(val=token.value)
            lexer.expect(TokenType.QUOTE)

        if lexer.peek().type == TokenType.RBRACE:
            break
        else:
            lexer.expect(TokenType.COMMA)

        yield EnumMember(name=name, value=value)


def generate_enum(e):
    yield 'enum {name} {{'.format(name=e.name)
    max_len = 0
    for m in e.members:
        if len(m.name) > max_len:
            max_len = len(m.name)
    for m in e.members:
        yield '    {name:{width}} = {value},'.format(
                name=m.name, width=max_len, value=m.value)
    yield '};'


# TODO(plesslie): check structs that they do match their bit/byte width
# sizes
def generate_struct_def(struct, types):
    """
    types: dict mapping known type names to C typename
    """
    yield 'struct {name} {{'.format(name=struct.name)
    for member in stuct.members:
        yield '{typedecl} {name};'.format(
                typedecl=types[member.name], name=member.name)
    yield '}'


def generate_struct(struct, types, typedefs):
    print('struct {name} {{'.format(name=struct.name))
    struct_width = 0
    outputs = []
    for member in struct.members:
        try:
            # TODO(plesslie): support making typedefs for array types
            name = typedefs[member.typedecl.name].name
        except:
            name = member.typedecl.name

        try:
            typedecl = types[name]
        except KeyError, ke:
            raise Exception("Unknown type {name}".format(name=ke))
        outputs.append((typedecl.ctype, typedecl.span, member.name))
        struct_width += typedecl.width * typedecl.span

    # insert this struct into our list of types
    types[struct.name] = BasicType(width=struct_width, span=1, signed=False,
            ctype=struct.name)

    max_len = 0
    for ctype, _, _ in outputs:
        if len(ctype) > max_len:
            max_len = len(ctype)
    for ctype, span, name in outputs:

        if span > 1:
            spanstr = '[{span}]'.format(span=span)
        else:
            spanstr = ''
        print('    {ctype:{width}} {name}{span};'.format(
            ctype=ctype, width=max_len, name=name, span=spanstr))
    print('};')

if __name__ == '__main__':
    with open('itch.idl') as f:
        lines = f.readlines()

    lexer = Tokenizer(lines)
    enums, structs, typedefs = parse(lexer)

    types = {} # name -> BasicType
    # TODO(plesslie): add types 'ts64', 'ts48', 'price64', 'price32'
    # TODO(plesslie): 5.4 and 8.4 prices?

    types['u8' ] = BasicType(width=8 , span=1, signed=False, ctype='uint8_t')
    types['u16'] = BasicType(width=16, span=1, signed=False, ctype='uint16_t')
    types['u32'] = BasicType(width=32, span=1, signed=False, ctype='uint32_t')
    types['u64'] = BasicType(width=64, span=1, signed=False, ctype='uint64_t')
    types['u48'] = BasicType(width=8 , span=4, signed=False, ctype='uint8_t')

    types['s8' ] = BasicType(width=8 , span=1, signed=True, ctype='int8_t')
    types['s16'] = BasicType(width=16, span=1, signed=True, ctype='int16_t')
    types['s32'] = BasicType(width=32, span=1, signed=True, ctype='int32_t')
    types['s64'] = BasicType(width=64, span=1, signed=True, ctype='int64_t')

    types['c8'] = BasicType(width=8, span=1, signed=True, ctype='char')

    print('#pragma once')
    print()
    print('#include <cstdint>')
    print()
    print("// File generated by wiregen.py - do not edit by hand")
    print()

    for enum in enums:
        # TODO(plesslie): support enums that aren't byte divisible
        width = enum.width if enum.width > 0 else 8
        if width < 8 or width > 64 or width % 8 != 0:
            raise Exception("not supporting enums with width: {}".format(
                width))
        ctype = 'uint{width}_t'.format(width=width)
        types[enum.name] = BasicType(width=width, span=1, signed=False,
                ctype=ctype)
        for ss in generate_enum(enum):
            print(ss)
        print()

    for struct in structs:
        generate_struct(struct, types, typedefs)
        print()

