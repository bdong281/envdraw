#!/usr/bin/env python3

import ast, inspect
from code import InteractiveConsole, compile_command
from examine2 import *

class EnvDrawConsole(InteractiveConsole):
    """InteractiveConsole for the EnvDraw program."""

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            if compile_command(source, filename, symbol):
                tree = ast.parse(source, filename, symbol)
                new_tree = ast.fix_missing_locations(AddFuncCall().visit(
                                                        AddFuncReturn().visit(
                                                            AddFuncDef().visit(tree))))
                compiled_code = compile(new_tree, filename, symbol)
                self.runcode(compiled_code)
                TRACKER.draw(inspect.currentframe())
                return False
            else:
                return InteractiveConsole.runsource(self, source, filename, symbol)
        except (SyntaxError, OverflowError):
            self.showsyntaxerror(filename)
            return False

    def runcode(self, code):
        #print("code:", code)
        return InteractiveConsole.runcode(self, code)

TRACKER = Tracker()
funcdef.tracker = TRACKER
funcreturn.tracker = TRACKER
funccall.tracker = TRACKER

if __name__ == "__main__":
    EnvDrawConsole().interact()
