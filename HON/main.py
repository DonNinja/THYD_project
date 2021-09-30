#
# Project HON: Main program
#
import ast
import symtable as ost
import sys
import os
from hon.parser import Parser, SyntaxErrorException
import hon.print_visitor as print_visitor
from hon.symtab_visitor import SymbolTableVisitor

files = os.listdir(sys.path[0] + '/test')
files.sort()
for file in files:
    with open(sys.path[0] + '/test/' + file) as f:
        if f.name != sys.path[0] + "/test/" + 'test_08.py':
            continue
        print('*' * 40)
        print("FILE:", f.name)
        print('*' * 40)
        try:
            parser = Parser(f)
            as_tree = parser.parse()
            visitor = print_visitor.PrintVisitor()
            visitor.visit(as_tree)
            st_visitor = SymbolTableVisitor()
            st = st_visitor.create_symtable(as_tree)
            st_visitor.disp_table(st)

        except SyntaxErrorException as e:
            print('SyntaxError:', e.message, e.location)
