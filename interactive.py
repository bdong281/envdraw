#!/usr/bin/env python3

"""Interactive front end for EnvDraw.

This was added by Tom Magrino (tmagrino@berkeley.edu)
"""

import ast, inspect
from code import InteractiveConsole, compile_command
from examine import *
from pprint import pprint

class EnvDrawConsole(InteractiveConsole):
    """InteractiveConsole for the EnvDraw program."""

    def runsource(self, source, filename="<input>", symbol="single"):
        """Do the same thing as any InteractiveConsole, except if we run into a
        completed statement, we first run the decoration code for envdraw on it
        before passing it off to the execute part of the REPL.
        """
        try:
            if compile_command(source, filename, symbol):
                tree = ast.parse(source, filename, symbol)
                new_tree = ast.fix_missing_locations(AddFuncCall().visit(
                                                        AddFuncReturn().visit(
                                                            AddFuncDef().visit(tree))))
                compiled_code = compile(new_tree, filename, symbol)
                self.runcode(compiled_code)
                TRACKER.draw(self.locals)
                return False
            else:
                return InteractiveConsole.runsource(self, source, filename, symbol)
        except (SyntaxError, OverflowError):
            self.showsyntaxerror(filename)
            return False


if __name__ == "__main__":
    # Add in bindings that we want to have "under the hood" in the interpreter
    local_bindings = {v : globals()[v] for v in IGNORE_VARS if v in
                      globals().keys()}
    EnvDrawConsole(locals=local_bindings).interact()
