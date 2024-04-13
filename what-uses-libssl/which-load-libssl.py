#!/usr/bin/python3

import json

data = json.load(open('graph.json', 'r'))

exes = data['dyns']
links = data['links']

def uses_libssl(e, memo={}):
    if e not in links:
        return False
    if e in memo:
        return memo[e]

    deps = links[e]
    for soname, path in deps.items():
        if soname.startswith('libssl.so') or uses_libssl(path):
            memo[e] = True
            return True

    memo[e] = False
    return False

for e in exes:
    if uses_libssl(e):
        print(e)
