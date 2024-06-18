#!/usr/bin/env python3

import subprocess
import json

list = subprocess.Popen(['find', '/', '-type', 'f', '-executable'], stdout=subprocess.PIPE, encoding='utf8')

dynamic_exes = {}
exe_links = {}

for bin in list.stdout.readlines():
    bin = bin.strip()
    if bin.startswith('/snap') or bin.startswith('/home'):
        continue
    file_output = subprocess.check_output(['file', bin], encoding='utf8')
    if 'dynamically linked' in file_output:
        dynamic_exes[bin] = file_output
    else:
        continue

    links = subprocess.run(['ldd', bin], encoding='utf8', check=False, capture_output=True).stdout.splitlines()
    for l in links:
        l = l.strip()
        if ' => ' in l:
            soname, _, path, _ = l.split()
            exe_links.setdefault(bin, {})[soname] = path

json.dump(dict(links=exe_links, dyns=dynamic_exes), open('graph.json', 'w'))
