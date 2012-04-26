import ast
import inspect
import gc
import sys
from pprint import pprint
from examine import *

FUNCTION_TYPE = type(lambda x: 0)

def _get_called_function():
    frame = inspect.currentframe().f_back.f_back
    code = frame.f_code
    global_obs = frame.f_globals
    for possible in gc.get_referrers(code):
        if type(possible) == FUNCTION_TYPE:
            return possible

class AddFuncDef(ast.NodeTransformer):
    """NodeTransformer for asts which takes each function defintion (either by
    a def statement or by a lambda expression) and uses the funcdef decorator
    with the function (as defined in examine.py).
    """

    def visit_FunctionDef(self, node):
        """Perform transformation on def statements.  Simply add the decorator
        to the function.
        """
        self.generic_visit(node)
        node.decorator_list.insert(0, ast.Name(id='funcdef', ctx=ast.Load()))
        return node

    def visit_Lambda(self, node):
        """Perform transformation on lambda expressions.  Set the value of the
        lambda to be the result of calling funcdef on the original function.
        """
        self.generic_visit(node)
        new = ast.Call(func=ast.Name(id='funcdef', ctx=ast.Load()), args=[node], keywords=[])
        return new

    
class AddFuncReturn(ast.NodeTransformer):
    """NodeTransformer for asts which takes each return statement and replaces
    'return expr' with 'return funcreturn(expr)'.
    """
    
    def visit_Return(self, node):
        """Take Return node and change the code in the ast from 'return expr'
        to 'return funcreturn(expr)'
        """
        self.generic_visit(node)
        new = ast.Call(func=ast.Name(id='funcreturn', ctx=ast.Load()), args=[node.value], keywords=[])
        node.value = new
        return node

    def visit_FunctionDef(self, node):
        """Take FunctionDef node and add an additional call to funcreturn at
        the end, just in case there's no return statement.
        """
        self.generic_visit(node)
        new = ast.Return(value=ast.Call(func=ast.Name(id='funcreturn',
                                                      ctx=ast.Load()),
                                        args=[ast.Name(id='None',
                                                       ctx=ast.Load())],
                                        keywords=[]))
        node.body.append(new)
        return node

    def visit_Lambda(self, node):
        """Perform the equivalent transformation on the result of the lambda
        statement's evaluation.
        """
        self.generic_visit(node)
        new_body = ast.Call(func=ast.Name(id='funcreturn', ctx=ast.Load()),
                            args=[node.body], keywords=[])
        node.body = new_body
        return node

class AddFuncCall(ast.NodeTransformer):
    """Modify function calls to start with a call to funccall."""

    def visit_FunctionDef(self, node):
        """Insert into the body of the function an initial call to funccall."""
        self.generic_visit(node)
        new = ast.Expr(value=ast.Call(func=ast.Name(id='funccall', ctx=ast.Load()), args=[], keywords=[]))
        node.body.insert(0, new)
        return node

    def visit_Lambda(self, node):
        """replace a lambda expression of the form:
            lambda args: expr
        with
            lambda args: (funccall(), expr)[1]
        To simulate the same effect as calling it at the beginning of the
        equivalent function definition and reference.
        """
        self.generic_visit(node)
        call_to_funccall = ast.Call(func=ast.Name(id='funccall',
                                                  ctx=ast.Load()), args=[],
                                    keywords=[])
        tuple_result = ast.Tuple(elts=[call_to_funccall, node.body],
                                 ctx=ast.Load())
        replacement = ast.Subscript(value=tuple_result,
                                    slice=ast.Index(value=ast.Num(n=1)),
                                    ctx=ast.Load())
        node.body = replacement
        return node


def envdraw_decorate(orig_ast):
    orig_ast = AddFuncDef().visit(orig_ast)
    orig_ast = AddFuncReturn().visit(orig_ast)
    orig_ast = AddFuncCall().visit(orig_ast)
    call_to_update = \
            ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='TRACKER',
                                                                      ctx=ast.Load()),
                                                       attr='insert_global_bindings',
                                                       ctx=ast.Load()),
                                    args=[ast.Call(func=ast.Name(id='locals',
                                                                 ctx=ast.Load()),
                                                   args=[], keywords=[])],
                                    keywords=[]))
    #orig_ast.body.append(call_to_update)
    return ast.fix_missing_locations(orig_ast)

if __name__ == '__main__':
    tree = ast.parse(open(sys.argv[1]).read())
    new_tree = envdraw_decorate(tree)
    pprint(ast.dump(new_tree))
    #compile(new_tree, '<unknown>', 'exec')
