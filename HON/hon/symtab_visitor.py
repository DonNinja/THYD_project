import functools
from symtable import symtable
from sys import flags
import hon.hast as ast
from hon import visitor
import hon.symbol_table as st


class SymbolTableVisitor(visitor.Visitor):
    #
    # TO DO: Implement a visitor to create and populate the symbol table(s).
    #
    ...

    def __init__(self):
        self.sym_table = None

    def disp_table(self, st):
        print("\nSymbol table:", st.get_name(), st.get_type())
        print(st.get_identifiers())
        if st.get_type() == 'function':
            print('parameters: ', st.get_parameters())
            print('locals', st.get_locals())
            print('globals', st.get_globals())
            print('nonlocals', st.get_nonlocals())

        print(st.get_symbols())
        for s in st.get_symbols():
            print('{:10s} l:{} g:{} p:{} r:{} n:{} i:{}'.format(
                s.get_name(),
                s.is_local(),
                s.is_global(),
                s.is_parameter(),
                s.is_referenced(),
                s.is_nonlocal(),
                s.is_imported()
            ))
            # assert(st.lookup(s.get_name()) is s)

        if st.has_children():
            for c in st.get_children():
                self.disp_table(c)
    # Use this function as the outside call to create the symbol table

    def create_symtable(self, node_ast_root):
        self.sym_table = st.SymbolTable('top', 'module')
        self.curr_table = self.sym_table
        self.do_visit(node_ast_root)
        return self.sym_table

    def do_visit(self, node):
        if node:
            self.visit(node)

    @functools.singledispatchmethod
    def visit(self, node):
        print("Visitor support missing for", type(node))
        exit()

    @visit.register
    def _(self, node: ast.VariableLValueNode):
        flags = 0
        if self.curr_table == self.sym_table:
            flags |= st.Symbol.Is.Global
        else:
            flags |= st.Symbol.Is.Local
        self.curr_table.add_entry(st.Symbol(node.name, flags))
        for expr in node.expr_list:
            self.do_visit(expr)

    @visit.register
    def _(self, node: ast.PassStmtNode):
        pass

    @visit.register
    def _(self, node: ast.BreakStmtNode):
        pass

    @visit.register
    def _(self, node: ast.ContinueStmtNode):
        pass

    @visit.register
    def _(self, node: ast.IfStmtNode):
        for expr, block in node.expr_block_list:
            self.do_visit(expr)
            self.do_visit(block)

    @visit.register
    def _(self, node: ast.WhileStmtNode):
        self.do_visit(node.expr)
        self.do_visit(node.block)

    @visit.register
    def _(self, node: ast.AssignStmtNode):
        self.do_visit(node.lvalue)
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.BlockStmtNode):
        for stmt in node.stmts:
            self.do_visit(stmt)

    @visit.register
    def _(self, node: ast.FunctionDefStmtNode):
        new_table = st.Function(node.name, 'function', node.params)

        for param in node.params:
            new_table.add_entry(st.Symbol(param, st.Symbol.Is.Local | st.Symbol.Is.Parameter))

        self.curr_table = new_table
        self.do_visit(node.block)
        self.sym_table.add_child(new_table)
        self.curr_table = self.sym_table

    @visit.register
    def _(self, node: ast.ReturnStmtNode):
        self.do_visit(node.expr)

    @visit.register
    def _(self, node: ast.OperatorExprNode):
        self.do_visit(node.lhs)
        self.do_visit(node.rhs)

    @visit.register
    def _(self, node: ast.VariableRValueExprNode):
        for expr in node.expr_list:
            self.do_visit(expr)

    @visit.register
    def _(self, node: ast.ValueExprNode):
        pass

    @visit.register
    def _(self, node: ast.ListExprNode):
        for expr in node.expr_list:
            self.do_visit(expr)

    @visit.register
    def _(self, node: ast.FunctionCallExprNode):
        for expr in node.expr_list:
            self.do_visit(expr)

    @visit.register
    def _(self, node: ast.MethodCallExprNode):
        for expr in node.expr_list:
            self.do_visit(expr)
