class Node:
    pass


class VariableLValueNode(Node):
    def __init__(self, name, expr_list):
        self.name = name
        self.expr_list = expr_list
        return


class StmtNode(Node):
    pass


class PassStmtNode(Node):
    pass


class BreakStmtNode(Node):
    pass


class ContinueStmtNode(Node):
    pass


class IfStmtNode(StmtNode):
    def __init__(self, expr_block_list):
        self.expr_block_list = expr_block_list
        return


class WhileStmtNode(StmtNode):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block
        return


class AssignStmtNode(StmtNode):
    def __init__(self, lvalue, expr):
        self.lvalue = lvalue
        self.expr = expr
        return


class BlockStmtNode(StmtNode):
    def __init__(self, stmts):
        self.stmts = stmts
        return


class FunctionDefStmtNode(StmtNode):
    def __init__(self, name, params, block):
        self.name = name
        self.params = params
        self.block = block
        return


class ReturnStmtNode(StmtNode):
    def __init__(self, expr=None):
        self.expr = expr
        return


class ExprNode(Node):
    pass


class OperatorExprNode(ExprNode):
    def __init__(self, token, lhs, rhs=None):
        self.token = token
        self.lhs = lhs
        self.rhs = rhs
        return


class VariableRValueExprNode(ExprNode):
    def __init__(self, name, expr_list):
        self.name = name
        self.expr_list = expr_list
        return


class ValueExprNode(ExprNode):
    def __init__(self, value):
        self.value = value
        return


class ListExprNode(ExprNode):
    def __init__(self, expr_list):
        self.expr_list = expr_list
        return


class FunctionCallExprNode(ExprNode):
    def __init__(self, name, expr_list):
        self.name = name
        self.expr_list = expr_list
        return


class MethodCallExprNode(ExprNode):
    def __init__(self, name, method, expr_list):
        self.name = name
        self.method = method
        self.expr_list = expr_list
        return
