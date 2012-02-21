import ast
import inspect
import gc

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
        node.decorator_list.insert(0, ast.Name(id='funcdef', ctx=ast.Load()))
        self.generic_visit(node)
        return node

    def visit_Lambda(self, node):
        """Perform transformation on lambda expressions.  Set the value of the
        lambda to be the result of calling funcdef on the original function.
        """
        new = ast.Call(func=ast.Name(id='funcdef', ctx=ast.Load()), args=[node], keywords=[])
        self.generic_visit(node)
        return new

    
class AddFuncReturn(ast.NodeTransformer):
    """NodeTransformer for asts which takes each return statement and replaces
    'return expr' with 'return funcreturn(expr)'.
    """
    
    def visit_Return(self, node):
        """Take Return node and change the code in the ast from 'return expr'
        to 'return funcreturn(expr)'
        """
        new = ast.Call(func=ast.Name(id='funcreturn', ctx=ast.Load()), args=[node.value], keywords=[])
        self.generic_visit(node)
        node.value = new
        return node

    def visit_FunctionDef(self, node):
        """Take FunctionDef node and add an additional call to funcreturn at
        the end, just in case there's no return statement...
        """
        new = ast.Return(value=ast.Call(func=ast.Name(id='funcreturn',
                                                      ctx=ast.Load()),
                                        args=[ast.Name(id='None',
                                                       ctx=ast.Load())],
                                        keywords=[]))
        self.generic_visit(node)
        node.body.append(new)
        return node

    def visit_Lambda(self, node):
        """Perform the equivalent transformation on the result of the lambda
        statement's evaluation.
        """
        new_body = ast.Call(func=ast.Name(id='funcreturn', ctx=ast.Load()),
                            args=[node.body], keywords=[])
        node.body = new_body
        self.generic_visit(node)
        return node

class AddFuncCall(ast.NodeTransformer):
    """Modify function calls to start with a call to funccall."""

    def visit_FunctionDef(self, node):
        """Insert into the body of the function an initial call to funccall."""
        new = ast.Expr(value=ast.Call(func=ast.Name(id='funccall', ctx=ast.Load()), args=[], keywords=[]))
        node.body.insert(0, new)
        self.generic_visit(node)
        return node

    def visit_Lambda(self, node):
        """replace a lambda expression of the form:
            lambda args: expr
        with
            lambda args: (funccall(), expr)[1]
        To simulate the same effect as calling it at the beginning of the
        equivalent function definition and reference.
        """
        call_to_funccall = ast.Call(func=ast.Name(id='funccall',
                                                  ctx=ast.Load()), args=[],
                                    keywords=[])
        tuple_result = ast.Tuple(elts=[call_to_funccall, node.body],
                                 ctx=ast.Load())
        replacement = ast.Subscript(value=tuple_result,
                                    slice=ast.Index(value=ast.Num(n=1)),
                                    ctx=ast.Load())
        node.body = replacement
        self.generic_visit(node)
        return node


if __name__ == '__main__':
    tree = ast.parse(open('test.py').read())
    new_tree = ast.fix_missing_locations(AddFuncReturn().visit(AddFuncDef().visit(tree)))

    exec(compile(new_tree, '<unknown>', 'exec'))
