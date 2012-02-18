import ast
import inspect
import gc

FUNCTION_TYPE = type(lambda x: 0)

def funccall():
    print(_get_called_function())
    pass

def funcdef(func):
    # do stuff here
    #print('def:', func)
    return func

def funcreturn(val):
    # do stuff here
    #print('return:', val)
    #print(inspect.currentframe().f_back.f_locals)
    #print(_get_called_function())
    return val

def _get_called_function():
    frame = inspect.currentframe().f_back.f_back
    code = frame.f_code
    global_obs = frame.f_globals
    for possible in gc.get_referrers(code):
        if type(possible) == type(lambda x: 0):
            return possible

class AddFuncDef(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        node.decorator_list.insert(0, ast.Name(id='funcdef', ctx=ast.Load()))
        self.generic_visit(node)
        return node

    def visit_Lambda(self, node):
        new = ast.Call(func=ast.Name(id='funcdef', ctx=ast.Load()), args=[node], keywords=[])
        self.generic_visit(node)
        return new

    
class AddFuncReturn(ast.NodeTransformer):
    
    def visit_Return(self, node):
        new = ast.Call(func=ast.Name(id='funcreturn', ctx=ast.Load()), args=[node.value], keywords=[])
        self.generic_visit(node)
        node.value = new
        return node

class AddFuncCall(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        new = ast.Expr(value=ast.Call(func=ast.Name(id='funccall', ctx=ast.Load()), args=[], keywords=[]))
        node.body.insert(0, new)
        return node
    

if __name__ == '__main__':
    tree = ast.parse(open('test.py').read())
    new_tree = ast.fix_missing_locations(AddFuncCall().visit(AddFuncReturn().visit(AddFuncDef().visit(tree))))

    exec(compile(new_tree, '<unknown>', 'exec'))
