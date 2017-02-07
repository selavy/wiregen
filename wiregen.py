#!/usr/bin/env python

from __future__ import print_function
import sys
from collections import namedtuple


Token = namedtuple('Token', ['type', 'value'])

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


def tokenizer(lines):
    for i, line in enumerate(lines):
        if not line or line[0] == '#':
            continue
        linenum = i + 1

        # hack to make str.split() correctly split on token
        line = line.replace('(', ' ( ')
        line = line.replace(')', ' ) ')
        line = line.replace('{', ' { ')
        line = line.replace('}', ' } ')
        line = line.replace(';', ' ; ')
        line = line.replace('=', ' = ')
        line = line.replace('[', ' [ ')
        line = line.replace(']', ' ] ')
        line = line.replace('"', ' " ')
        line = line.replace("'", " ' ")
        line = line.replace(',', ' , ')
        for token in line.split():
            if token == 'enum':
                yield Token(type=TokenType.KWENUM, value=token)
            elif token == 'struct':
                yield Token(type=TokenType.KWSTRUCT, value=token)
            elif token == 'bits':
                yield Token(type=TokenType.KWBITS, value=token)
            elif token == '(':
                yield Token(type=TokenType.LPAREN, value=token)
            elif token == ')':
                yield Token(type=TokenType.RPAREN, value=token)
            elif token == '{':
                yield Token(type=TokenType.LBRACE, value=token)
            elif token == '}':
                yield Token(type=TokenType.RBRACE, value=token)
            elif token == ';':
                yield Token(type=TokenType.SEMICOLON, value=token)
            elif token == '=':
                yield Token(type=TokenType.EQUALS, value=token)
            elif token == '[':
                yield Token(type=TokenType.LSQBRACKET, value=token)
            elif token == ']':
                yield Token(type=TokenType.RSQBRACKET, value=token)
            elif token == "'" or token == '"':
                yield Token(type=TokenType.QUOTE, value=token)
            elif token == ',':
                yield Token(type=TokenType.COMMA, value=token)
            elif token.isdigit():
                yield Token(type=TokenType.NUMBER, value=int(token))
            elif is_ident(token):
                yield Token(type=TokenType.IDENT, value=token)
            else:
                raise Exception("Syntax Error on line {}: '{}'".format(
                    linenum, token))


#    for linenum, line in enumerate(lines):
#        # TODO(plesslie): fix this hack for adding comments
#        if not line or line[0] == '/' and line[1] == '/':
#            continue
#
#        token = ''
#        for i, c in enumerate(line):
#            if c.isspace():
#                continue
#            elif c == '/':
#                if line[i+1] == '/':
#                    continue
#                else:
#                    raise Exception("Stray '/' character on line {}".format(
#                        linenum+1))
#            elif c == 'e':
#                if line[i+1] == 'n' and line[i+2] == 'u' and line[i+3] == 'm':
#                    yield Token(type=TokenType.KWENUM, value='enum')
#            else:
#                raise Exception('Invalid token on line {}, column {}'.format(
#                    linenum+1, i))

if __name__ == '__main__':
    with open('itch.idl') as f:
        lines = f.readlines()

    for token in tokenizer(lines):
        print(token)
