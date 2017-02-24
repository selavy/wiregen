#!/usr/bin/env python

from __future__ import print_function
import sys


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
    KWBITS = 12
    KWBYTES = 13
    COLON = 14
    EQUALS = 15
    UNK = 16
    WHITESPACE = 17
    SQUOTE = 18

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
        elif t == TokenType.KWBITS:
            return 'bits'
        elif t == TokenType.KWBYTES:
            return 'bytes'
        elif t == TokenType.COLON:
            return ':'
        elif t == TokenType.EQUALS:
            return '='
        elif t == TokenType.WHITESPACE:
            return 'whitespace'
        elif t == TokenType.SQUOTE:
            return "'"
        else:
            raise Exception('Unknown type: {}'.format(t))

class Token(object):
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def __str__(self):
        return 'Token({typ}) = "{val}"'.format(
                typ=TokenType.tostr(self.type_), val=self.value)


def parse_file(f):
    pass

def _tokenize(stream):
    cur = ''
    type_ = TokenType.UNK

    for c in stream:
        if type_ == TokenType.UNK:
            if c == '(':
                yield Token(TokenType.LPAREN, c)
            elif c == ')':
                yield Token(TokenType.RPAREN, c)
            elif c == '[':
                yield Token(TokenType.LBRACKET, c)
            elif c == ']':
                yield Token(TokenType.RBRACKET, c)
            elif c == '{':
                yield Token(TokenType.LBRACE, c)
            elif c == '}':
                yield Token(TokenType.RBRACE, c)
            elif c == ':':
                yield Token(TokenType.COLON, c)
            elif c == ',':
                yield Token(TokenType.COMMA, c)
            elif c == '=':
                yield Token(TokenType.EQUALS, c)
            elif c == "'":
                yield Token(TokenType.SQUOTE, c)
            elif c == ';':
                yield Token(TokenType.SEMICOLON, c)
            elif c == '"':
                cur = c
                type_ = TokenType.STRING
            elif c.isspace():
                cur = c
                type_ = TokenType.WHITESPACE
            elif c.isdigit():
                cur = c
                type_ = TokenType.INTEGER
            elif c.isalpha():
                cur = c
                type_ = TokenType.IDENT
            else:
                raise Exception('Invalid character: {}'.format(c))
        elif type_ == TokenType.STRING:
            if c == '"':
                yield Token(TokenType.STRING, cur)
                cur = ''
                type_ = TokenType.UNK
            else:
                cur += c
        elif type_ == TokenType.WHITESPACE:
            if c.isspace():
                cur += c
            else:
                yield Token(TokenType.WHITESPACE, cur)
                cur = ''
                type_ = TokenType.UNK
        elif type_ == TokenType.INTEGER:
            if c.isdigit():
                cur += c
            else:
                yield Token(TokenType.INTEGER, cur)
                cur = ''
                type_ = TokenType.UNK
        elif type_ == TokenType.IDENT:
            if c.isalpha() or c.isdigit() or c == '_':
                cur += c
                continue
            elif cur == 'enum':
                yield Token(TokenType.KWENUM, cur)
            elif cur == 'bits':
                yield Token(TokenType.KWBITS, cur)
            elif cur == 'bytes':
                yield Token(TokenType.KWBYTES, cur)
            else:
                yield Token(TokenType.IDENT, cur)
            cur = ''
            type_ = TokenType.UNK
        else:
            raise Exception('Unknown type {}'.format(type_))


if __name__ == '__main__':
    with open('itch5x.idl') as f:
        lines = f.readlines()
    lines = '\n'.join(lines)
    for token in _tokenize(lines):
        print(token)
