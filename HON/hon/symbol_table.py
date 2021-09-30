#
#  Symbol table.
#
#  TO DO: Implement the classes below.
#         You are free to decide on the internal implementation.
#         You can add members as needed, both methods (including __init__) and variables, but you are not
#         allowed to remove or change the interface to the existing methods.
#         See https://docs.python.org/3.8/library/symtable.html for details.
#

from enum import IntFlag

class Symbol:
    """
    An entry in a SymbolTable corresponding to an identifier in the source. The constructor is not public.
    """

    class Is(IntFlag):
        Imported = 16
        Parameter = 8
        Referenced = 4
        Global = 2
        Local = 1
    
    def __init__(self, name, flags):
        self._name = name
        self.flags = flags

    def __repr__(self) -> str:
        return f"<symbol '{self._name}'>"

    def get_name(self):
        """
        Return the table’s name. This is the name of the class if the table is for a class, 
        the name of the function if the table is for a function,
        or 'top' if the table is global (get_type() returns 'module').

        Return the symbol’s name.
        """
        return self._name

    def is_referenced(self):
        """
        Return True if the symbol is used in its block.
        """
        return bool(self.flags & Symbol.Is.Referenced)

    def is_imported(self):
        """
        Return True if the symbol is created from an import statement.
        (Ignore for now)
        """
        return bool(self.flags & Symbol.Is.Imported)

    def is_parameter(self):
        """
        Return True if the symbol is a parameter.
        """
        return bool(self.flags & Symbol.Is.Parameter)

    def is_global(self):
        """
        Return True if the symbol is global.
        """
        return bool(self.flags & Symbol.Is.Global)

    def is_local(self):
        """
        Return True if the symbol is local.
        """
        return bool(self.flags & Symbol.Is.Local)

    def is_nonlocal(self):
        """
        Return True if the symbol is nonlocal.
        """
        return bool(not(self.flags & Symbol.Is.Local))


class SymbolTable:
    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._symbols = {}
        self._children = []

    def get_type(self):
        """
        Return the type of the symbol table. Possible values are 'class', 'module', and 'function'.
        """
        return self._type

    def get_name(self):
        """
        Return the table’s name. This is the name of the class if the table is for a class, the name
        of the function if the table is for a function, or 'top' if the table is global (get_type() returns 'module').
        """
        return self._name

    def is_nested(self):
        """
        Return True if the block is a nested class or function.
        """
        return not(self._name == "top")

    def has_children(self):
        """
        Return True if the block has nested namespaces within it. These can be obtained with get_children().
        """
        return len(self.get_children()) > 0

    def get_identifiers(self):
        """
        Return a list of names of symbols in this table.
        """
        return list(self._symbols.keys())

    def lookup(self, name):
        """
        Lookup name in the table and return a Symbol instance.
        """
        return self._symbols[name]

    def get_symbols(self):
        """
        Return a list of Symbol instances for names in the table.
        """
        return list(self._symbols.values())

    def get_children(self):
        """
        Return a list of the nested symbol tables.
        """
        return list(self._children)
    
    def add_entry(self, symbol):
        """ Add an entry to the symbol table """
        self._symbols[symbol.get_name()] = symbol

    def add_child(self, st):
        """ Add a child symbol table to the symbol table """
        self._children.append(st)


class Function(SymbolTable):
    """
    A namespace for a function or method. This class inherits SymbolTable.
    """
    def __init__(self, name, type, parameters):
        super().__init__(name, type)
        self._params = parameters

    def get_parameters(self):
        """
        Return a tuple containing names of parameters to this function.
        """
        return tuple(self._params)

    def get_locals(self):
        """
        Return a tuple containing names of locals in this function.
        """
        ret_lis = []
        for sym in self.get_symbols():
            if sym.is_local():
                ret_lis.append(sym.get_name())
        return tuple(ret_lis)

    def get_globals(self):
        """
        Return a tuple containing names of globals in this function.
        """
        ret_lis = []
        for sym in self.get_symbols():
            if sym.is_global():
                ret_lis.append(sym.get_name())
        return tuple(ret_lis)

    def get_nonlocals(self):
        """
        Return a tuple containing names of non_locals in this function.
        """
        ret_lis = []
        for sym in self.get_symbols():
            if sym.is_global():
                ret_lis.append(sym.get_name())
        return tuple(ret_lis)
