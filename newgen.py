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
    COMMENT = 11
    KWENUM = 12
    KWBITS = 13
    KWBYTES = 14

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
        elif t == TokenType.COMMENT:
            return 'comment'
        elif t == TokenType.KWENUM:
            return 'enum'
        elif t == TokenType.KWBITS:
            return 'bits'
        elif t == TokenType.KWBYTES:
            return 'bytes'
        else:
            raise Exception('Unknown type: {}'.format(t))


def parse_file(f):
    pass


if __name__ == '__main__':
    with open('itch5x.idl') as f:
        parse_file(f)
