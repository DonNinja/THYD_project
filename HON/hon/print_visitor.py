import functools
import hon.hast as ast
from hon import visitor


class PrintVisitor(visitor.Visitor):

    def __init__(self):
        self.indent = 0

    def do_visit(self, node):
        if node:
            self.visit(node)

    def print(self, text):
        for _ in range(self.indent):
            print('   ', sep='', end='')
        print(text)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.VariableLValueNode):
        self.print(f'(variable {node.name})')
        self.indent += 1
        for expr in node.expr_list:
            self.do_visit(expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.PassStmtNode):
        self.print('(pass)')

    @visit.register
    def _(self, node: ast.BreakStmtNode):
        self.print('(break)')

    @visit.register
    def _(self, node: ast.ContinueStmtNode):
        self.print('(continue)')

    @visit.register
    def _(self, node: ast.IfStmtNode):
        self.print('(if)')
        self.indent += 1
        for expr, block in node.expr_block_list:
            self.do_visit(expr)
            self.do_visit(block)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.print('(while)')
        self.indent += 1
        self.do_visit(node.expr)
        self.do_visit(node.block)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        self.print('=')
        self.indent += 1
        self.do_visit(node.lvalue)
        self.do_visit(node.expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.BlockStmtNode):
        self.print('(block)')
        self.indent += 1
        for stmt in node.stmts:
            self.do_visit(stmt)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.FunctionDefStmtNode):
        self.print(f'def {node.name}({node.params}):')
        self.indent += 1
        self.do_visit(node.block)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.print('return')
        self.indent += 1
        self.do_visit(node.expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.OperatorExprNode):
        self.print(f'op = {node.token}')
        self.indent += 1
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.VariableRValueExprNode):
        self.print(f'(variable {node.name})')
        self.indent += 1
        for expr in node.expr_list:
            self.do_visit(expr)
        self.indent -= 1

    @visit.register
    def _(self, node: ast.ValueExprNode):
        self.print(f'({node.value} {type(node.value)})')

    @visit.register
    def _(self, node: ast.ListExprNode):
        self.print('[')
        self.indent += 1
        for expr in node.expr_list:
            self.do_visit(expr)
        self.indent -= 1
        self.print(']')

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        self.print(f'{node.name}(')
        self.indent += 1
        for expr in node.expr_list:
            self.do_visit(expr)
        self.indent -= 1
        self.print(')')

    @visit.register
    def _(self, node: ast.MethodCallExprNode):
        self.print(f'{node.name}.{node.method}(')
        self.indent += 1
        for expr in node.expr_list:
            self.do_visit(expr)
        self.indent -= 1
        self.print(')')
