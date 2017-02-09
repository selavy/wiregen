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
    EOF = 15

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
        elif token == TokenType.LSQBRACKET:
            return '['
        elif token == TokenType.RSQBRACKET:
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

    while 1:
        token = lexer.peek()
        if lexer.accept(TokenType.KWENUM):
            enum = parse_enum(lexer)
            enums.append(enum)
        elif lexer.accept(TokenType.EOF):
            break
        else:
            raise Exception("SyntaxError({}): Invalid token '{}'".format(
                token.linum, token.value))
    return enums, structs


#def parse_struct(lexer):
#    if lexer.accept(TokenType.KWBITS):
#        if not lexer.accept(TokenType.LPAREN):
#            raise Exception("Expected '(' after keyword 'bits'")
#
#        width = lexer.peek().value
#        if not lexer.accept(TokenType.NUMBER):
#            raise Exception("Expected number after keyword 'bits'")
#
#        if not lexer.accept(TokenType.RPAREN):
#            raise Exception("Expected ')'")



def parse_enum(lexer):
    if lexer.accept(TokenType.KWBITS):
        lexer.expect(TokenType.LPAREN)
        #if not lexer.accept(TokenType.LPAREN):
        #    raise Exception("Expected '(' after keyword 'bits'")

        token = lexer.peek()
        #if not lexer.accept(TokenType.NUMBER):
        #    raise Exception("Expected number after keyword 'bits")
        lexer.expect(TokenType.NUMBER)

        width = token.value
        if not lexer.accept(TokenType.RPAREN):
            raise Exception("Expected ')' to close 'bits' declaration")

    token = lexer.peek()
    if not lexer.accept(TokenType.IDENT):
        raise Exception("Expected name after 'enum' keyword")
    name = token.value

    if not lexer.accept(TokenType.LBRACE):
        raise Exception("Expected '{' to being enum declaration")

    members = []
    for member in parse_enum_member(lexer):
        members.append(member)

    if not members:
        raise Exception("Enum '{}' declared with no values!".format(
            name))

    if not lexer.accept(TokenType.RBRACE):
        raise Exception("Expected '}}' to finish enum declaration, instead "
                "received: '{}' on line {}".format(token.value, token.linum))

    return Enum(name=name, width=width, members=members)


def parse_enum_member(lexer):
    while 1:
        # allow comma after last member
        if lexer.peek().type == TokenType.RBRACE:
            return

        token  = lexer.peek()
        name = token.value
        if not lexer.accept(TokenType.IDENT):
            raise Exception("SyntaxError({}): Expected enum member name, instead received '{}'".format(token.linum, token.value))

        if not lexer.accept(TokenType.EQUALS):
            raise Exception("Expected '=' after enum name to give value")

        token = lexer.peek()
        if lexer.accept(TokenType.NUMBER):
            value = token.value
        elif lexer.accept(TokenType.QUOTE):
            token = lexer.peek()
            if not lexer.accept(TokenType.IDENT):
                raise Exception("Invalid enum value: '{}'".format(token.value))
            if len(token.value) != 1 or not token.value.isalpha():
                raise Exception("Invalid enum value: '{}'".format(token.value))
            value = "'{val}'".format(val=token.value)

            if not lexer.accept(TokenType.QUOTE):
                raise Exception("Mismatched quotes on enum value")

        if lexer.peek().type == TokenType.RBRACE:
            break
        elif not lexer.accept(TokenType.COMMA):
            raise Exception("Expected comma between enum declarations")

        yield EnumMember(name=name, value=value)


if __name__ == '__main__':
    with open('itch.idl') as f:
        lines = f.readlines()

    lexer = Tokenizer(lines)
    enums, structs = parse(lexer)
    pprint.pprint(enums)
    pprint.pprint(structs)

