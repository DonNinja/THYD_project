#
# Project ON: Main program
#
from onparser import Parser, ParserSyntaxError
import print_visitor

with open('test.on') as f:
    """
    lexer = onlexer.Lexer(f)
    token_tuple = lexer.next()
    while token_tuple.token != onlexer.Token.EOI:
        print(token_tuple)
        token_tuple = lexer.next()
    print(token_tuple)
    """
    try:
        parser = Parser(f)
        as_tree = parser.parse()
        visitor = print_visitor.PrintVisitor()
        visitor.visit(as_tree)
    except ParserSyntaxError as e:
        print(e.message, e.location)


