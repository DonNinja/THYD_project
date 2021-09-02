import onast as ast
from onlexer_sol import Lexer, Token


class ParserSyntaxError(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.location = loc


class Parser:

    def __init__(self, line):
        self.lexer = Lexer(line)
        self.token_tuple = self.lexer.next()
        return

    def match(self, token):  # helper routine.
        if self.token_tuple.token == token:
            self.token_tuple = self.lexer.next()
        else:
            text = "Syntax error: expected {:s} but got {:s} ({:s}).".format(token,
                                                                             self.token_tuple.token,
                                                                             self.token_tuple.lexeme)
            raise ParserSyntaxError(text, self.token_tuple.location)

    def match_if(self, token):  # helper routine.
        if self.token_tuple.token == token:
            self.match(token)
            return True
        return False

    def parse(self):
        statements = []
        while self.token_tuple.token != Token.EOI:
            stmt = self.stmt()
            statements.append(stmt)
        self.match(Token.EOI)
        return ast.BlockStmtNode(statements)

    def stmt(self):
        if self.token_tuple.token in {Token.KwIf, Token.KwWhile}:
            stmt = self.compound_stmt()
        else:
            stmt = self.simple_stmt()
            self.match(Token.Semicolon)
        return stmt

    def simple_stmt(self):
        # Add missing code ...
        return None

    def compound_stmt(self):
        # Add missing code ...
        return None

    def if_stmt(self):
        expr_block_list = []
        self.match(Token.KwIf)
        self.match(Token.ParenthesisL)
        expr = self.expression()
        self.match(Token.ParenthesisR)
        block = self.block()
        expr_block_list.append((expr, block))
        while self.match_if(Token.KwElif):
            self.match(Token.ParenthesisL)
            expr = self.expression()
            self.match(Token.ParenthesisR)
            block = self.block()
            expr_block_list.append((expr, block))
        if self.match_if(Token.KwElse):  # Match 'else' to the previous 'if'.
            expr = ast.ValueExprNode(True)
            block = self.block()
        else:
            expr = ast.ValueExprNode(False)
            block = None
        expr_block_list.append((expr, block))
        return ast.IfStmtNode(expr_block_list)

    def while_stmt(self):
        # Add missing code ...
        return None

    def assign_stmt(self):
        # Add missing code ...
        return None

    def block(self):
        statements = []
        if self.match_if(Token.CurlyBracketL):
            while self.token_tuple.token != Token.CurlyBracketR:
                stmt = self.stmt()
                statements.append(stmt)
            self.match(Token.CurlyBracketR)
        else:
            stmt = self.stmt()
            statements.append(stmt)
        return ast.BlockStmtNode(statements)

    def expression(self):
        # Add missing code ...
        return None

    def or_expression(self):
        # Add missing code ...
        return None

    def and_expression(self):
        # Add missing code ...
        return None

    def not_expression(self):
        # Add missing code ...
        return None

    def comparison(self):
        expr = self.arithmetic_expr()
        if self.token_tuple.token in {Token.OpLt, Token.OpGt,Token.OpEq, Token.OpGtEq, Token.OpLtEq, Token.OpNotEq}:
            token = self.token_tuple.token
            self.match(self.token_tuple.token)
            rhs = self.arithmetic_expr()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def arithmetic_expr(self):
        # Add missing code ...
        return None

    def term(self):
        # Add missing code ...
        return None

    def factor(self):
        # Add missing code ...
        return None

    def atom(self):
        if self.match_if(Token.ParenthesisL):
            expr = self.expression()
            self.match(Token.ParenthesisR)
        elif self.match_if(Token.KwTrue):
            expr = ast.ValueExprNode(True)
        elif self.match_if(Token.KwFalse):
            expr = ast.ValueExprNode(False)
        elif self.match_if(Token.KwNone):
            expr = ast.ValueExprNode(None)
        elif self.token_tuple.token == Token.Number:
            expr = ast.ValueExprNode(int(self.token_tuple.lexeme))
            self.match(Token.Number)
        elif self.token_tuple.token == Token.String:
            expr = ast.ValueExprNode(self.token_tuple.lexeme)
            self.match(Token.String)
        else:
            expr = self.variable()
        return expr

    def variable(self):
        name = self.token_tuple.lexeme
        self.match(Token.Identifier)
        return ast.VariableRValueExprNode(name)
