#!/usr/bin/env python

from __future__ import print_function
import sys
from collections import namedtuple
import pprint


Token = namedtuple('Token', ['type', 'value', 'linum'])
Enum = namedtuple('Enum', ['name', 'width', 'members'])
EnumMember = namedtuple('EnumMember', ['name', 'value'])


class TokenType(object):
    KWENUM = 0
    KWSTRUCT = 1
    LBRACE = 2
    RBRACE = 3
    LPAREN = 4
    RPAREN = 5
    SEMICOLON = 6
    EQUALS = 7
    LSQBRACKET = 8
    RSQBRACKET = 9
    QUOTE = 10
    NUMBER = 11
    IDENT = 12
    COMMA = 13
    KWBITS = 14


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
                yield Token(type=TokenType.LSQBRACKET, value=token, linum=linum)
            elif token == ']':
                yield Token(type=TokenType.RSQBRACKET, value=token, linum=linum)
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


# struct_decl ::= 'struct' size_decl name '{' members_decl '}'
#               | 'struct' name '{' members_decl '}'
#               ;
#
# size_decl ::= 'bits' '(' number ')';
#
# members_decl ::= type name ';';
#
# enum_decl ::= 'enum' size_decl name '{' enum_members_decl '}';
#
# enum_members_decl ::= enum_members_decl ',' enum_members_decl
#                     | name '=' "'" IDENT "'"
#                     | name '=' number
#                     ;
#
# name ::= IDENT;


class Tokenizer(object):

    def __init__(self, lines):
        self.tokens = _tokenize(lines)
        self.token = self.tokens.next()

    def peek(self):
        return self.token

    def next(self):
        self.token = self.tokens.next()
        return self.token


def parse(lexer):
    enums = []
    structs = []

    try:
        while 1:
            token = lexer.peek()
            if token.type == TokenType.KWENUM:
                enums.append(parse_enum(lexer))
                token = lexer.next()
            else:
                raise Exception("Invalid token: {}".format(token))
    except StopIteration:
        return enums, structs

    raise Exception("Should never get here")


def parse_enum(lexer):
    token = lexer.next()
    if token.type == TokenType.KWBITS:
        token = lexer.next()
        if token.type != TokenType.LPAREN:
            raise Exception("Expected '(' after keyword 'bits'")
        token = lexer.next()
        if token.type != TokenType.NUMBER:
            raise Exception("Expected number after keyword 'bits")
        width = token.value
        token = lexer.next()
        if token.type != TokenType.RPAREN:
            raise Exception("Expected ')' after to close'bits' declaration")
        token = lexer.next()

    if token.type != TokenType.IDENT:
        raise Exception("Expected name after 'enum' keyword")

    name = token.value

    token = lexer.next()
    if token.type != TokenType.LBRACE:
        raise Exception("Expected '{' to being enum declaration")

    lexer.next()
    members = []
    for member in parse_enum_member(lexer):
        members.append(member)

    if not members:
        raise Exception("Enum '{}' declared with no values!".format(
            name))

    token = lexer.peek()
    if token.type != TokenType.RBRACE:
        raise Exception("Expected '}}' to finish enum declaration, instead "
                "received: '{}' on line {}".format(token.value, token.linum))

    return Enum(name=name, width=width, members=members)


def parse_enum_member(lexer):
    token = lexer.peek()
    while 1:
        if token.type == TokenType.RBRACE:
            return

        if token.type != TokenType.IDENT:
            raise Exception("Expected enum member name, instead received '{}'".format(token.value))
        else:
            name = token.value

        token = lexer.next()
        if token.type != TokenType.EQUALS:
            raise Exception("Expected '=' after enum name to give value")

        token = lexer.next()
        if token.type == TokenType.NUMBER:
            value = token.value
        elif token.type == TokenType.QUOTE:
            token = lexer.next()
            if token.type != TokenType.IDENT:
                raise Exception("Invalid enum value: '{}'".format(token.value))
            if len(token.value) != 1 or not token.value.isalpha():
                raise Exception("Invalid enum value: '{}'".format(token.value))
            value = "'{val}'".format(val=token.value)

            token = lexer.next()
            if token.type != TokenType.QUOTE:
                raise Exception("Mismatched quotes on enum value")

        yield EnumMember(name=name, value=value)

        token = lexer.next()
        if token.type == TokenType.COMMA:
            token = lexer.next()



if __name__ == '__main__':
    with open('itch.idl') as f:
        lines = f.readlines()

    lexer = Tokenizer(lines)
    enums, structs = parse(lexer)
    pprint.pprint(enums)
    pprint.pprint(structs)

