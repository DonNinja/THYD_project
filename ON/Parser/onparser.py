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
        if self.match_if(Token.KwLet):
            return self.assign_stmt()
        elif self.match_if(Token.KwPass):
            return ast.PassStmtNode()
        elif self.match_if(Token.KwBreak):
            return ast.BreakStmtNode()
        elif self.match_if(Token.KwContinue):
            return ast.ContinueStmtNode()
        return None

    def compound_stmt(self):
        if self.token_tuple.token == Token.KwIf:
            return self.if_stmt()
        elif self.token_tuple.token == Token.KwWhile:
            return self.while_stmt()
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
        self.match(Token.KwWhile)
        self.match(Token.ParenthesisL)
        expr = self.expression()
        self.match(Token.ParenthesisR)
        block = self.block()

        return ast.WhileStmtNode(expr, block)

    def assign_stmt(self):
        name = self.token_tuple.lexeme
        self.match(Token.Identifier)
        self.match(Token.OpAssign)
        expr = self.expression()
        return ast.AssignStmtNode(ast.VariableLValueNode(name), expr)

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
        return self.or_expression()
        # return ast.OperatorExprNode(Token.OpOr, or_expr)

    def or_expression(self):
        expr = self.and_expression()
        while self.token_tuple.token == Token.OpOr:
            token = self.token_tuple.token
            self.match(Token.OpOr)
            rhs = self.and_expression()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def and_expression(self):
        expr = self.not_expression()
        while self.token_tuple.token == Token.OpAnd:
            token = self.token_tuple.token
            self.match(Token.OpAnd)
            rhs = self.not_expression()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def not_expression(self):
        if self.match_if(Token.OpNot):
            return self.not_expression()
        else:
            return self.comparison()

    def comparison(self):
        expr = self.arithmetic_expr()
        if self.token_tuple.token in {Token.OpLt, Token.OpGt, Token.OpEq, Token.OpGtEq, Token.OpLtEq, Token.OpNotEq}:
            token = self.token_tuple.token
            self.match(self.token_tuple.token)
            rhs = self.arithmetic_expr()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def arithmetic_expr(self):
        expr = self.term()
        while self.token_tuple.token in {Token.OpPlus, Token.OpMinus}:
            token = self.token_tuple.token
            self.match(token)
            rhs = self.term()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def term(self):
        expr = self.factor()
        while self.token_tuple.token in {Token.OpMultiply, Token.OpDivide, Token.OpModulus, Token.OpIntDivide}:
            token = self.token_tuple.token
            self.match(token)
            rhs = self.factor()
            expr = ast.OperatorExprNode(token, expr, rhs)
        return expr

    def factor(self):
        if self.token_tuple.token in {Token.OpPlus, Token.OpMinus}:
            token = self.token_tuple.token
            self.match(token)
            expr = self.factor()
            return ast.OperatorExprNode(token, expr)
        else:
            return self.atom()

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
