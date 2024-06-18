#!/usr/bin/env python3

import json
import sys
import subprocess

bin = sys.argv[-1]

data = json.load(open('data.json', 'r'))

try:
    proc = subprocess.run([bin, '-v'], env=dict(LD_DEBUG='all'), encoding='utf8', capture_output=True, timeout=2, check=False)
    stderr = proc.stderr
except subprocess.TimeoutExpired as e:
    stderr = e.stderr.decode('utf8')

bindings = []

for line in stderr.splitlines():
    if 'binding file' not in line:
        continue

    print(line)
    bits = line.split()
    pid, _, _, src, _, _, dst = bits[:7]
    if len(bits) == 12:
        a, b, sym, vers = bits[-4:]
    else:
        vers = None
        a, b, sym = bits[-3:]
    assert (a, b) == ('normal', 'symbol')
    if vers:
        vers = vers[1:-1]
    sym = sym[1:-1]

    if 'libssl' in dst:
        bindings.append(dict(src=src, dst=dst, sym=sym, vers=vers))

data[bin] = bindings
json.dump(data, open('data.json', 'w'))
