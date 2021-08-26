# Main program
import onlexer as lexer
from onlexer import Token, LexerError

with open('test.on') as f:
    try:
        lexer = lexer.Lexer(f)
        token_tuple = lexer.next()
        while token_tuple.token != Token.EOI:
            print(token_tuple)
            token_tuple = lexer.next()
        print(token_tuple)
    except LexerError as e:
        print("Lexer error:", e.message, e.location)

