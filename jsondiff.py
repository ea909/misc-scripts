#!/usr/bin/env python3
"""
jsondiff is a utility for listing the differences between two json files.
Usage 1: jsondiff file_a file_b
Usage 2: jsondiff file_a file_b -l

It can operate in two differents modes: object and list mode (list mode is
Usage 2, with the -l flag).

In object mode, jsondiff outputs a new json object which merges all of the
common structure between file_a and file_b. At points where file_a and file_b
differ, an object is inserted with the following structure:
    {
        A_SIDE: <contents from file_a at this point>,
        B_SIDE: <contents from file_b at this point>
    }

In list mode, jsondiff outputs a listing of all of the leaf node differences
between the two files. The listing is a table with three columns:
    1. A breadcrumb showing the object tree navigation to the point of the
    difference.
    2. The file_b value.
    3. The file_a value.

This is a pretty simple utility so it will break if your JSON actually has
'A_SIDE' and 'B_SIDE' keys in it. You can change the keys below to something
that will work.
"""
# LICENSE:
# Copyright 2018 Eric Alzheimer
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
import json
from pprint import pprint
from itertools import zip_longest
__author__    = "Eric Alzheimer"
__copyright__ = "Copyright 2018 Eric Alzheimer"
__license__   = "MIT"

A_SIDE = "A_SIDE"
B_SIDE = "B_SIDE"

def difference(a_side, b_side):
    if b_side is None: # Only B exists
        return { A_SIDE: a_side }
    elif a_side is None: # Only A exists
        return { B_SIDE: b_side }
    # Differing types, cannot sub-compare:
    elif type(a_side) != type(b_side): 
        return { A_SIDE: a_side, B_SIDE: b_side }
    # Compare keys, build dict of differences:
    elif type(a_side) == dict: 
        return { key : difference(a_side.get(key), b_side.get(key)) 
                 for key in set(a_side) | set(b_side) }
    # Compare list items, build list of differences:
    elif type(a_side) == list: 
        return [difference(a, b) for a, b in zip_longest(a_side, b_side)]
    # Equal leaf nodes are untouched:
    elif a_side == b_side:
        return a_side
    # Show difference in unequal leaf nodes:
    else:
        return { A_SIDE: a_side, B_SIDE: b_side }

def list_differences(diff, key_stack=None):
    if key_stack is None:
        key_stack = []
    if type(diff) == dict:
        if B_SIDE in diff or A_SIDE in diff:
            print(":".join(key_stack) + "\t{0}\t{1}".format(diff.get(B_SIDE), diff.get(A_SIDE)))
        else:
            for key in diff:
                key_stack.append(key)
                list_differences(diff[key], key_stack)
                key_stack.pop()
    elif type(diff) == list:
        for i, v in enumerate(diff):
            key_stack.append("List[{0}]".format(i))
            list_differences(v, key_stack)
            key_stack.pop()

def usage():
    print("Usage: jsondiff.py file_a file_b [-l]")
    print("Produces an object or a list showing the differences in two json objects")
    print("Example: jsondiff.py file_a file_b -l")
    print("    Lists every differing leaf node of between json objects, showing the breadcrumb to reach it")
    print("    First column is the breadcrumb")
    print("    Second column is the file_b value")
    print("    Third column is the file_a value")
    print("Example: jsondiff.py file_a file_b")
    print("    Prints a json object where differences are replaced with an object with two fields:")
    print('        "A_SIDE" -> Value in file_a')
    print('        "B_SIDE" -> Value in file_b')

def main():
    if len(sys.argv) < 3:
        usage()
        return
    with open(sys.argv[1]) as file_a:
        obj_a = json.load(file_a)
    with open(sys.argv[2]) as file_b:
        obj_b = json.load(file_b)

    diff = difference(obj_a, obj_b)

    if len(sys.argv) > 3 and sys.argv[3] == "-l":
        list_differences(diff)
    else:
        pprint(diff)

if __name__ == "__main__":
    main()

