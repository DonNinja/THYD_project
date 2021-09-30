#
# T-603-THYD Compilers
# Project: Lexer for language version ON (solution).
#
from enum import Enum
from typing import NamedTuple


# The tokens the Lexer recognizes.
class Token(Enum):
    EOI = 0
    Unknown = 1

    # Keywords
    KwLet = 2  # let
    KwPass = 3  # pass
    KwBreak = 4  # break
    KwContinue = 5  # continue
    KwIf = 6  # if
    KwElif = 7  # elif
    KwElse = 8  # else
    KwWhile = 9  # while
    KwNone = 10  # None
    KwTrue = 11  # True
    KwFalse = 12  # False
    KwDef = 13  # def
    KwReturn = 15  # return

    # Operators
    OpOr = 20     # or
    OpAnd = 21    # and
    OpNot = 22    # not
    OpLt = 23    # <
    OpGt = 24     # >
    OpEq = 25     # ==
    OpGtEq = 26   # >=
    OpLtEq = 27   # <=
    OpNotEq = 28  # !=
    OpPlus = 29   # +
    OpMinus = 30  # -
    OpMultiply = 31   # *
    OpDivide = 32     # /
    OpModulus = 33    # %
    OpIntDivide = 34  # //
    OpAssign = 35     # =
    OpPower = 36      # **

    # Punctuation marks
    Semicolon = 40  # ;
    ParenthesisL = 41  # (
    ParenthesisR = 42  # )
    BracketL = 43  # [
    BracketR = 44  # ]
    CurlyBracketL = 45  # {
    CurlyBracketR = 46  # }
    Comma = 47  # ,
    Period = 48  # .
    Colon = 49  # :

    # Other
    IntegerLiteral = 60  # digits (see project description)
    FloatLiteral = 61  # digits (see project description)
    # '...' or "..." (see project description, throw a  LexerError if unterminated string)
    StringLiteral = 62
    Identifier = 63  # name (see project description)
    Indent = 64
    Dedent = 65
    Newline = 66


class Location(NamedTuple):
    line: int
    col: int


class TokenTuple(NamedTuple):
    token: Token
    lexeme: str
    location: Location


class SyntaxErrorException(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.location = loc


class Lexer:
    __reserved_words = {
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
        "def": Token.KwDef,
        "return": Token.KwReturn,
        "or": Token.OpOr,
        "and": Token.OpAnd,
        "not": Token.OpNot
    }

    def __read_next_char(self):
        """
        Private helper routine. Reads the next input character, while keeping
        track of its location within the input file.
        """
        if self.__eof:
            self.ch = ''
            return

        if self.ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.ch = self.f.read(1)

        if not self.ch:  # eof
            self.ch = '\n'
            self.line += 1
            self.col = 1
            self.__eof = True

    def __init__(self, f):
        """
        Constructor for the lexer.
        :param f: handle to the input file (from open('filename')).
        """
        self.f, self.ch, self.line, self.col = f, '', 1, 0
        self.open_brackets = 0
        self.legal_indent_levels = [1]
        self.__last_token = None
        self.__eof = False
        self.__read_next_char()

    def next(self):
        """
        Match the next token in input.
        :return: TokenTuple with information about the matched token.
        """

        # Remove white-spaces and comments, if any, before matching next token.
        bf_loc = Location(self.line, self.col)
        removed = True
        while removed:
            removed = False
            white_spaces = {' ', '\t', '\n', '\r'} if self.open_brackets > 0 else {
                ' ', '\t', '\r'}
            while self.ch in white_spaces:
                self.__read_next_char()
                removed = True
            if self.ch == '#':
                while self.ch and self.ch not in {'\n'}:
                    self.__read_next_char()
                removed = True
            # Lines with only ws and comments are ignored.
            if bf_loc.col == 1 and (self.ch == '\n' and not self.__eof):
                self.__read_next_char()
                removed = True

        # Record the start location of the lexeme we're matching.
        loc = Location(self.line, self.col)

        # Ensure indentation is correct, emitting INDENT/DEDENT tokens as called for.
        # At start of a new logical line.
        if self.__last_token in {Token.Newline, Token.Dedent}:
            if loc.col > self.legal_indent_levels[-1]:
                self.legal_indent_levels.append(loc.col)
                self.__last_token = Token.Indent
                return TokenTuple(Token.Indent, '<INDENT>', loc)
            elif loc.col < self.legal_indent_levels[-1]:
                self.legal_indent_levels.pop()
                if loc.col > self.legal_indent_levels[-1]:
                    raise SyntaxErrorException('IndentationError: dedent does not match any outer indentation level',
                                               loc)
                self.__last_token = Token.Dedent
                return TokenTuple(Token.Dedent, '<DEDENT>', loc)

        # Now, try to match a lexeme.
        if self.ch == '':
            token_tuple = TokenTuple(Token.EOI, '', loc)
        elif self.ch == '<':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpLtEq, '<=', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpLt, '<', loc)
        elif self.ch == '>':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpGtEq, '>=', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpGt, '>', loc)
        elif self.ch == '+':
            token_tuple = TokenTuple(Token.OpPlus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '-':
            token_tuple = TokenTuple(Token.OpMinus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '*':
            self.__read_next_char()
            if self.ch == '*':
                token_tuple = TokenTuple(Token.OpPower, '**', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpMultiply, '*', loc)
        elif self.ch == '/':
            self.__read_next_char()
            if self.ch == '/':
                token_tuple = TokenTuple(Token.OpIntDivide, '//', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpDivide, '/', loc)
        elif self.ch == '%':
            token_tuple = TokenTuple(Token.OpModulus, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '=':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpEq, '==', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.OpAssign, '=', loc)
        elif self.ch == '!':
            self.__read_next_char()
            if self.ch == '=':
                token_tuple = TokenTuple(Token.OpNotEq, '!=', loc)
                self.__read_next_char()
            else:
                token_tuple = TokenTuple(Token.Unknown, '!', loc)
        elif self.ch == ';':
            token_tuple = TokenTuple(Token.Semicolon, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '(':
            token_tuple = TokenTuple(Token.ParenthesisL, self.ch, loc)
            self.open_brackets += 1
            self.__read_next_char()
        elif self.ch == ')':
            token_tuple = TokenTuple(Token.ParenthesisR, self.ch, loc)
            self.open_brackets -= 1
            self.__read_next_char()
        elif self.ch == '[':
            token_tuple = TokenTuple(Token.BracketL, self.ch, loc)
            self.open_brackets += 1
            self.__read_next_char()
        elif self.ch == ']':
            token_tuple = TokenTuple(Token.BracketR, self.ch, loc)
            self.open_brackets -= 1
            self.__read_next_char()
        elif self.ch == '{':
            token_tuple = TokenTuple(Token.CurlyBracketL, self.ch, loc)
            self.open_brackets += 1
            self.__read_next_char()
        elif self.ch == '}':
            token_tuple = TokenTuple(Token.CurlyBracketR, self.ch, loc)
            self.open_brackets -= 1
            self.__read_next_char()
        elif self.ch == ',':
            token_tuple = TokenTuple(Token.Comma, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '.':
            chars = [self.ch]
            self.__read_next_char()
            if self.ch.isdigit():
                if self.float_literal(chars):
                    token_tuple = TokenTuple(
                        Token.FloatLiteral, ''.join(chars), loc)
                else:
                    raise SyntaxErrorException(
                        "Invalid floating-point literal", loc)
            else:
                token_tuple = TokenTuple(Token.Period, self.ch, loc)
        elif self.ch == ':':
            token_tuple = TokenTuple(Token.Colon, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '\n':
            token_tuple = TokenTuple(Token.Newline, self.ch, loc)
            self.__read_next_char()
        elif self.ch == '"' or self.ch == "'":
            quote = self.ch
            self.__read_next_char()
            chars = []
            while self.ch and self.ch not in {'\n', quote}:
                chars.append(self.ch)
                self.__read_next_char()
            if self.ch == '\n':
                raise SyntaxErrorException("Unterminated string", loc)
            text = ''.join(chars)
            token_tuple = TokenTuple(Token.StringLiteral, text, loc)
            self.__read_next_char()
        else:
            if self.ch.isalpha() or self.ch == '_':
                # Match an identifier.
                chars = [self.ch]
                self.__read_next_char()
                while self.ch.isalnum() or self.ch == '_':
                    chars.append(self.ch)
                    self.__read_next_char()
                name = ''.join(chars)
                token_tuple = TokenTuple(self.__reserved_words.get(
                    name, Token.Identifier), name, loc)
            elif self.ch.isdigit():
                # Match a number literal.
                chars = []
                while self.ch.isdigit():
                    chars.append(self.ch)
                    self.__read_next_char()
                if self.ch in {'.', 'e', 'E'}:
                    chars.append(self.ch)
                    self.__read_next_char()
                    if self.float_literal(chars):
                        token_tuple = TokenTuple(
                            Token.FloatLiteral, ''.join(chars), loc)
                    else:
                        raise SyntaxErrorException(
                            "Invalid floating-point literal", loc)
                else:
                    token_tuple = TokenTuple(
                        Token.IntegerLiteral, ''.join(chars), loc)
            else:
                token_tuple = TokenTuple(Token.Unknown, self.ch, loc)
                self.__read_next_char()

        self.__last_token = token_tuple.token
        return token_tuple

    def float_literal(self, chars):
        """
        Matches a Python-style floating-point literal.
        TODO: You should update this method to support Python-style floating-point literals.
               (except, you may omit the '_' character (has no semantic meaning, only there for visual effect.)
          See: https://docs.python.org/3.8/reference/lexical_analysis.html#floating-point-literals
        :param chars: List of already matched characters (in), list of all matched characters (out).
        :return: True if a valid literal matches, otherwise False.
        """
        while self.ch.isdigit():
            chars.append(self.ch)
            self.__read_next_char()
        if self.ch in { "e", "E", "-", "+" }:
            chars.append(self.ch)
            self.__read_next_char()
            return self.float_literal(chars)
        elif self.ch == ".":
            return False
        return True
