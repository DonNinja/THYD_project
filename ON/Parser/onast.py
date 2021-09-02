class Node:
    pass


class VariableLValueNode(Node):
    def __init__(self, lvalue):
        self.lvalue = lvalue
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


class ExprNode(Node):
    pass


class OperatorExprNode(ExprNode):
    def __init__(self, token, lhs, rhs = None):
        self.token = token
        self.lhs = lhs
        self.rhs = rhs
        return


class VariableRValueExprNode(ExprNode):
    def __init__(self, variable):
        self.variable = variable
        return


class ValueExprNode(ExprNode):
    def __init__(self, value):
        self.value = value
        return

