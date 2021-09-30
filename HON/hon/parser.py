import hon.hast as hast
from hon.lexer import Lexer, Token, SyntaxErrorException


class Parser:

    def __init__(self, line):
        self.lexer = Lexer(line)
        self.token_tuple = self.lexer.next()
        self.peek_token_tuple = None
        return

    def next_token(self):
        if self.peek_token_tuple is not None:
            token_tuple = self.peek_token_tuple
            self.peek_token_tuple = None
        else:
            token_tuple = self.lexer.next()
        return token_tuple

    def peek(self):  # helper routine
        if self.peek_token_tuple is None:
            if self.token_tuple.token != Token.EOI:
                self.peek_token_tuple = self.next_token()
            else:
                self.peek_token_tuple = self.token_tuple
        return self.peek_token_tuple

    def match(self, token):  # helper routine.
        if self.token_tuple.token == token:
            self.token_tuple = self.next_token()
        else:
            text = "Syntax error: expected {:s} but got {:s} ({:s}).".format(token,
                                                                             self.token_tuple.token,
                                                                             self.token_tuple.lexeme)
            raise SyntaxErrorException(text, self.token_tuple.location)

    def match_if(self, token):  # helper routine.
        if self.token_tuple.token == token:
            self.match(token)
            return True
        return False

    def parse(self):
        statements = []
        while self.token_tuple.token != Token.EOI:
            if self.match_if(Token.Newline):
                continue
            if self.token_tuple.token == Token.KwDef:
                s = self.function_def()
                statements.append(s)
            else:
                stmts = self.stmt()
                for s in stmts:
                    statements.append(s)
        self.match(Token.EOI)
        return hast.BlockStmtNode(statements)

    def function_def(self):
        self.match(Token.KwDef)
        name = self.token_tuple.lexeme
        self.match(Token.Identifier)
        self.match(Token.ParenthesisL)
        params = self.param_list()
        self.match(Token.ParenthesisR)
        self.match(Token.Colon)
        def_block = self.block()
        return hast.FunctionDefStmtNode(name, params, def_block)

    def param_list(self):
        params = [self.token_tuple.lexeme]
        self.match(Token.Identifier)
        while self.match_if(Token.Comma):
            params.append(self.token_tuple.lexeme)
            self.match(Token.Identifier)
        return params

    def stmt(self):
        if self.token_tuple.token in {Token.KwIf, Token.KwWhile}:
            stmt = [self.compound_stmt()]
        else:
            stmt = self.simple_stmt()
        return stmt

    def simple_stmt(self):
        stmt = self.small_stmt()
        stmts = [stmt]
        while self.match_if(Token.Semicolon):
            if self.token_tuple.token == Token.Newline or \
               self.token_tuple.token == Token.EOI:
                break
            stmt = self.small_stmt()
            stmts.append(stmt)
        self.match(Token.Newline)
        return stmts

    def small_stmt(self):
        if self.match_if(Token.KwPass):
            stmt = hast.PassStmtNode()
        elif self.match_if(Token.KwBreak):
            stmt = hast.BreakStmtNode()
        elif self.match_if(Token.KwContinue):
            stmt = hast.ContinueStmtNode()
        elif self.token_tuple.token == Token.KwReturn:
            stmt = self.return_stmt()
        else:
            peek_token = self.peek().token
            if peek_token == Token.ParenthesisL:
                print("Function call")
                stmt = self.function_call()
            elif peek_token == Token.Period:
                print("Method call")
                stmt = self.method_call()
            else:
                stmt = self.assign_stmt()
        return stmt

    def compound_stmt(self):
        if self.token_tuple.token == Token.KwIf:
            stmt = self.if_stmt()
        else:
            stmt = self.while_stmt()
        return stmt

    def if_stmt(self):
        expr_block_list = []
        self.match(Token.KwIf)
        expr = self.expression()
        self.match(Token.Colon)
        block = self.block()
        expr_block_list.append((expr, block))
        while self.match_if(Token.KwElif):
            expr = self.expression()
            self.match(Token.Colon)
            block = self.block()
            expr_block_list.append((expr, block))
        if self.match_if(Token.KwElse):  # Match 'else' to the previous 'if'.
            self.match(Token.Colon)
            expr = hast.ValueExprNode(True)
            block = self.block()
        else:
            expr = hast.ValueExprNode(False)
            block = None
        expr_block_list.append((expr, block))
        return hast.IfStmtNode(expr_block_list)

    def while_stmt(self):
        self.match(Token.KwWhile)
        expr = self.expression()
        self.match(Token.Colon)
        block = self.block()
        return hast.WhileStmtNode(expr, block)

    def assign_stmt(self):
        # self.match(Token.KwLet)
        lvalue = self.variable(lvalue=True)
        self.match(Token.OpAssign)
        expr = self.expression()
        return hast.AssignStmtNode(lvalue, expr)

    def return_stmt(self):
        self.match(Token.KwReturn)
        if self.token_tuple.token not in {Token.Newline, Token.EOI}:
            expr = self.expression()
        else:
            expr = None
        return hast.ReturnStmtNode(expr)

    def block(self):
        if self.match_if(Token.Newline):
            statements = []
            self.match(Token.Indent)
            while self.token_tuple.token != Token.Dedent:
                stmts = self.stmt()
                for s in stmts:
                    statements.append(s)
            self.match(Token.Dedent)
        else:
            statements = self.simple_stmt()
        return hast.BlockStmtNode(statements)

    def expression(self):
        return self.or_expression()

    def or_expression(self):
        expr = self.and_expression()
        while self.match_if(Token.OpOr):
            rhs = self.and_expression()
            expr = hast.OperatorExprNode(Token.OpOr, expr, rhs)
        return expr

    def and_expression(self):
        expr = self.not_expression()
        while self.match_if(Token.OpAnd):
            rhs = self.not_expression()
            expr = hast.OperatorExprNode(Token.OpAnd, expr, rhs)
        return expr

    def not_expression(self):
        if self.match_if(Token.OpNot):
            expr = self.not_expression()
            expr = hast.OperatorExprNode(Token.OpNot, expr)
        else:
            expr = self.comparison()
        return expr

    def comparison(self):
        expr = self.arithmetic_expr()
        if self.token_tuple.token in {Token.OpLt, Token.OpGt, Token.OpEq, Token.OpGtEq, Token.OpLtEq, Token.OpNotEq}:
            token = self.token_tuple.token
            self.match(self.token_tuple.token)
            rhs = self.arithmetic_expr()
            expr = hast.OperatorExprNode(token, expr, rhs)
        return expr

    def arithmetic_expr(self):
        expr = self.term()
        while self.token_tuple.token in {Token.OpPlus, Token.OpMinus}:
            token = self.token_tuple.token
            self.match(self.token_tuple.token)
            rhs = self.term()
            expr = hast.OperatorExprNode(token, expr, rhs)
        return expr

    def term(self):
        expr = self.factor()
        while self.token_tuple.token in {Token.OpMultiply, Token.OpDivide, Token.OpModulus, Token.OpIntDivide}:
            token = self.token_tuple.token
            self.match(self.token_tuple.token)
            rhs = self.factor()
            expr = hast.OperatorExprNode(token, expr, rhs)
        return expr

    def factor(self):
        if self.token_tuple.token in {Token.OpPlus, Token.OpMinus}:
            op_token = self.token_tuple.token
            self.match(self.token_tuple.token)
            expr = self.factor()
            expr = hast.OperatorExprNode(op_token, expr)
        else:
            expr = self.power()
        return expr

    def power(self):
        expr = self.atom()
        if self.match_if(Token.OpPower):
            rhs = self.factor()
            expr = hast.OperatorExprNode(Token.OpPower, expr, rhs)
        return expr

    def atom(self):
        if self.match_if(Token.ParenthesisL):
            expr = self.expression()
            self.match(Token.ParenthesisR)
        elif self.match_if(Token.BracketL):
            if self.token_tuple.token != Token.BracketR:
                list_of_expr = self.expr_list()
            else:
                list_of_expr = []
            expr = hast.ListExprNode(list_of_expr)
            self.match(Token.BracketR)
        elif self.match_if(Token.KwTrue):
            expr = hast.ValueExprNode(True)
        elif self.match_if(Token.KwFalse):
            expr = hast.ValueExprNode(False)
        elif self.match_if(Token.KwNone):
            expr = hast.ValueExprNode(None)
        elif self.token_tuple.token == Token.IntegerLiteral:
            expr = hast.ValueExprNode(int(self.token_tuple.lexeme))
            self.match(Token.IntegerLiteral)
        elif self.token_tuple.token == Token.FloatLiteral:
            expr = hast.ValueExprNode(float(self.token_tuple.lexeme))
            self.match(Token.FloatLiteral)
        elif self.token_tuple.token == Token.StringLiteral:
            expr = hast.ValueExprNode(self.token_tuple.lexeme)
            self.match(Token.StringLiteral)
        else:
            if self.peek().token == Token.ParenthesisL:
                expr = self.function_call()
            elif self.peek().token == Token.Period:
                expr = self.method_call()
            else:
                expr = self.variable()
        return expr

    def variable(self, name=None, lvalue=False):
        if name is None:        # If name is not None, then identifier already matched.
            name = self.token_tuple.lexeme
            self.match(Token.Identifier)
        expr_list = []
        while self.match_if(Token.BracketL):
            expr = self.expression()
            expr_list.append(expr)
            self.match(Token.BracketR)
        return hast.VariableLValueNode(name, expr_list) if lvalue else hast.VariableRValueExprNode(name, expr_list)

    def function_call(self, name=None):
        if name is None:        # If name is not None, then identifier already matched.
            name = self.token_tuple.lexeme
            self.match(Token.Identifier)
        self.match(Token.ParenthesisL)
        if self.token_tuple.token != Token.ParenthesisR:
            list_of_expr = self.expr_list()
        else:
            list_of_expr = []
        self.match(Token.ParenthesisR)
        return hast.FunctionCallExprNode(name, list_of_expr)

    def method_call(self, name=None):
        if name is None:        # If name is not None, then identifier already matched.
            name = self.token_tuple.lexeme
            self.match(Token.Identifier)
        self.match(Token.Period)
        method = self.token_tuple.lexeme
        self.match(Token.Identifier)
        self.match(Token.ParenthesisL)
        if self.token_tuple.token != Token.ParenthesisR:
            list_of_expr = self.expr_list()
        else:
            list_of_expr = []
        self.match(Token.ParenthesisR)
        return hast.MethodCallExprNode(name, method, list_of_expr)

    def expr_list(self):
        exprs = [self.expression()]
        while self.match_if(Token.Comma):
            exprs.append(self.expression())
        return exprs
