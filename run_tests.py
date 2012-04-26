#!/usr/bin/env python3
"""Runs all specified tests for the envdraw program.

Written by Tom Magrino
"""

import sys, os, examine

def run_tests(files_or_directories):
    results = {}
    number_ran, number_passed = 0, 0
    while files_or_directories:
        filename = files_or_directories.pop(0)
        if os.path.isdir(filename):
            internal_files = [os.path.join(filename, dfile) for dfile in
                              os.listdir(filename)]
            files_or_directories.extend(internal_files)
        elif ".py" == os.path.basename(filename)[-3:]:
            print("Running test:", filename)
            print("-" * 80)
            with open(filename) as f:
                print(f.read())
            print("-" * 80)
            examine.run(filename, locals(), wait=False)
            number_ran += 1

            correct = '?'
            while correct not in ('y','n'):
                correct = input("Is this correct? [y/n] ").lower()
            results[filename] = (correct == 'y')
            if results[filename]:
                number_passed += 1
    print("Results:")
    for filename, passed in results.items():
        print("        {0}: {1}".format(filename, passed))
    print("{0}/{1} tests passed.".format(number_passed, number_ran))

if __name__ == "__main__":
    run_tests(sys.argv[1:])
