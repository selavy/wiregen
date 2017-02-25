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
    size = len(stream)
    i = 0
    while 1:
        while i < size and stream[i].isspace():
            i += 1
        if not (i < size):
            break

        c = stream[i]
        i += 1

        if c == '(':
            yield Token(TokenType.LPAREN, '(')
        elif c == ')':
            yield Token(TokenType.RPAREN, ')')
        elif c == '[':
            yield Token(TokenType.LBRACKET, '[')
        elif c == ']':
            yield Token(TokenType.RBRACKET, ']')
        elif c == '{':
            yield Token(TokenType.LBRACE, '{')
        elif c == '}':
            yield Token(TokenType.RBRACE, '}')
        elif c == ':':
            yield Token(TokenType.COLON, ':')
        elif c == ',':
            yield Token(TokenType.COMMA, ',')
        elif c == '=':
            yield Token(TokenType.EQUALS, '=')
        elif c == "'":
            yield Token(TokenType.SQUOTE, "'")
        elif c == ';':
            yield Token(TokenType.SEMICOLON, ';')
        elif c == '"':
            val = c
            while i < size and stream[i] != '"':
                c += stream[i]
                i += 1
            if i >= size:
                raise Exception('''Unmatched '"' character''')
            i += 1
            yield Token(TokenType.STRING, val)
        else:
            val = c
            while i < size:
                c = stream[i]
                if not (c.isalpha() or c.isdigit() or c == '_'):
                    break
                val += c
                i += 1
            if val == 'enum':
                yield Token(TokenType.KWENUM, val)
            elif val == 'bits':
                yield Token(TokenType.KWBITS, val)
            elif val == 'bytes':
                yield Token(TokenType.KWBYTES, val)
            else:
                yield Token(TokenType.IDENT, val)


if __name__ == '__main__':
    with open('itch5x.idl') as f:
        lines = f.readlines()
    lines = '\n'.join(lines)
    for token in _tokenize(lines):
        print(token)
