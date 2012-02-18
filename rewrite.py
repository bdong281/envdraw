import ast

class AddImport(ast.NodeTransformer):

    def visit_Module(self, node):
        node.body.insert(
            0,
            ast.Import(names=[ast.alias(name='envdraw2')]))
        return node
                      

class AddDecorator(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        node.decorator_list.insert(0, ast.Attribute(value=ast.Name(id='envdraw2', ctx=ast.Load()), attr='test', ctx=ast.Load()))
        self.generic_visit(node)
        return node
                

if __name__ == '__main__':
    tree = ast.parse(open('test.py').read())
    new_tree = ast.fix_missing_locations(AddDecorator().visit(AddImport().visit(tree)))
    
    eval(compile(new_tree, 'test.py', 'exec'))
