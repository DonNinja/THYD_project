#
# T-603-THYD Compilers
# Project: Lexer skeleton for language version ON.
#
from enum import Enum
from typing import NamedTuple


# The tokens the Lexer recognizes.
class Token(Enum):

    EOI = 0
    Unknown = 1

    # Keywords
    KwLet = 2           # let
    KwPass = 3          # pass
    KwBreak = 4         # break
    KwContinue = 5      # continue
    KwIf = 6            # if
    KwElif = 7          # elif
    KwElse = 8          # else
    KwWhile = 9         # while
    KwNone = 10         # None
    KwTrue = 11         # True
    KwFalse = 12        # False

    # Operators
    OpOr = 13           # or
    OpAnd = 14          # and
    OpNot = 15          # not
    OpLt = 16           # <
    OpGt = 17           # >
    OpEq = 18           # ==
    OpGtEq = 19         # >=
    OpLtEg = 20         # <=
    OpNotEq = 21        # !=
    OpPlus = 22         # +
    OpMinus = 23        # -
    OpMultiply = 24     # *
    OpDivide = 25       # /
    OpModulus = 26      # %
    OpIntDivide = 27    # //
    OpAssign = 28       # =

    # Punctuation marks
    Semicolon = 29      # ;
    ParenthesisL = 30   # (
    ParenthesisR = 31   # )
    CurlyBracketL = 32  # {
    CurlyBracketR = 33  # }

    # Other
    Number = 34         # digits (see project description)
    String = 35         # '...' or "..." (see project description, throw a
                        #                 LexerError if unterminated string)
    Identifier = 36     # name (see project description)


class Location(NamedTuple):
    line: int
    col: int


class TokenTuple(NamedTuple):
    token: Token
    lexeme: str
    location: Location


class LexerError(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.location = loc

class Lexer:

    __keywords = {
        "let": Token.KwLet,
        "pass": Token.KwPass,
        "break": Token.KwBreak,
        "continue": Token.KwContinue,
        "if": Token.KwIf,
        "elif": Token.KwElif,
        "else": Token.KwElse,
        "while": Token.KwWhile,
        "None": Token.KwNone,
        "True": Token.KwTrue,
        "False": Token.KwFalse,
        "or": Token.OpOr,
        "and": Token.OpAnd,
        "not": Token.OpNot
    }

    __punct_marks = {
        ";": Token.Semicolon,
        "(": Token.ParenthesisL,
        ")": Token.ParenthesisR,
        "{": Token.CurlyBracketL,
        "}": Token.CurlyBracketR
    }

    def __read_next_char(self):
        """
        Private helper routine. Reads the next input character, while keeping
        track of its location within the input file.
        """
        self.ch = self.f.read(1)
        if self.ch == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1

    def __init__(self, f):
        """
        Constructor for the lexer.
        :param f: handle to the input file (from open('filename')).
        """
        self.f, self.ch, self.line, self.col = f, '', 1, 0
        self.__read_next_char()

    def next(self):
        """
        Match the next token in input.
        :return: TokenTuple with information about the matched token.
        """
        # Remove white-spaces, if any, before matching next token.
        while self.ch in {'\n', ' ', '\t', '\r'}:
            self.__read_next_char()

        while self.ch == '#': # Until we reach an actual line, not a comment
            while self.ch != '\n':
                self.__read_next_char()
            self.__read_next_char()

        # Record the start location of the lexeme we're matching.
        loc = Location(self.line, self.col)

        # Now, try to match a lexeme.
        if self.ch == '':
            token_tuple = TokenTuple(Token.EOI, '', loc)
        elif self.ch == '+':
            token_tuple = TokenTuple(Token.OpPlus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '-':
            token_tuple = TokenTuple(Token.OpMinus, '-', loc)
            self.__read_next_char()
        elif self.ch == '/':
            self.__read_next_char()
            if self.ch == '/':
                token_tuple = TokenTuple(Token.OpIntDivide, '//', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpDivide, '/', loc)
        elif self.ch == '%':
            token_tuple = TokenTuple(Token.OpModulus, '%', loc)
            self.__read_next_char()
        elif self.ch == '*':
            token_tuple = TokenTuple(Token.OpMultiply, '*', loc)
            self.__read_next_char()
        elif self.ch == '<':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpLtEg, '<=', loc)
            else:
                token_tuple = TokenTuple(Token.OpLt, '<', loc)
        elif self.ch == '>':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpGtEq, '>=', loc)
            else:
                token_tuple = TokenTuple(Token.OpGt, '>', loc)
        elif self.ch == '=':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpEq, '==', loc)
            else:
                token_tuple = TokenTuple(Token.OpAssign, '=', loc)
        elif self.ch == '!':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpNotEq, '!=', loc)
        else:
            if self.ch.isalpha() or self.ch == '_':
                # Match an identifier.

                chars = [self.ch]
                self.__read_next_char()
                while self.ch.isalnum() or self.ch == '_':
                    chars.append(self.ch)
                    self.__read_next_char()
                name = ''.join(chars)
                token_tuple = TokenTuple(self.__keywords.get(name, Token.Identifier), name, loc)
            elif self.ch.isdigit():
                # Match a number.
                chars = []
                while self.ch.isdigit():
                    chars.append(self.ch)
                    self.__read_next_char()
                token_tuple = TokenTuple(Token.Number, ''.join(chars), loc)
                # Match a string
            elif self.ch == "'":
                chars = [self.ch]
                self.__read_next_char()

                while self.ch != "'":
                    chars.append(self.ch)
                    self.__read_next_char()
                    if self.ch in {'\n', ''}:
                        raise LexerError("String is not terminated at", loc)
                
                chars.append(self.ch)
                token_tuple = TokenTuple(Token.String, ''.join(chars), loc)
                self.__read_next_char()
            elif self.ch == '"':
                chars = [self.ch]
                self.__read_next_char()

                while self.ch != '"':
                    chars.append(self.ch)
                    self.__read_next_char()
                    if self.ch in {'\n', ''}:
                        raise LexerError("String is not terminated at", loc)

                chars.append(self.ch)
                token_tuple = TokenTuple(Token.String, ''.join(chars), loc)
                self.__read_next_char()
            else:
                # Match punctuation
                token_tuple = TokenTuple(self.__punct_marks.get(self.ch, Token.Unknown), self.ch, loc)
                self.__read_next_char()
        return token_tuple
