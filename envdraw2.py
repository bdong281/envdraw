import ast
import inspect
import gc

FUNCTION_TYPE = type(lambda x: 0)

def funcdef(func):
    # do stuff here
    #print('def:', func)
    return func

def funcreturn(val):
    # do stuff here
    #print('return:', val)
    #print(inspect.currentframe().f_back.f_locals)
    frame = inspect.currentframe().f_back
    code = frame.f_code
        #print(dir(code))
    global_obs = frame.f_globals
    result = None
    for possible in gc.get_referrers(code):
        if type(possible) == FUNCTION_TYPE:
            result = possible
            break
    print(possible)
    return val

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
    

if __name__ == '__main__':
    tree = ast.parse(open('test.py').read())
    new_tree = ast.fix_missing_locations(AddFuncReturn().visit(AddFuncDef().visit(tree)))

    exec(compile(new_tree, '<unknown>', 'exec'))
