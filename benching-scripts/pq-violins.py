import matplotlib.pyplot as plt
import numpy as np
import json

import slice

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
plt.rcParams["font.size"] = 8


def read_samples(filename):
    js = json.load(open(filename))

    r = []

    for iter, time in zip(js["iters"], js["times"]):
        r.extend([time / iter * 1e-3] * int(iter))
    r.sort()
    return r


for arch in ["amd64", "arm64"]:
    f, _ = plt.subplots(figsize=(9, 3), dpi=200)
    x25519 = read_samples(arch + "/clienthello/X25519/new/sample.json")
    mlkem_opt = read_samples(arch + "/clienthello/X25519MLKEM768/new/sample.json")
    mlkem_noopt = read_samples(
        arch + "/clienthello/X25519MLKEM768+X25519/new/sample.json"
    )
    data = [mlkem_noopt, mlkem_opt, x25519]
    plt.violinplot(data, vert=False, showextrema=False, showmedians=True, widths=1)
    labels = [
        "X25519MLKEM768, X25519",
        "X25519MLKEM768, X25519 optimized",
        "X25519 alone",
    ]
    dmax = int(max(max(x) for x in data)) + 10
    plt.yticks(range(1, len(labels) + 1), labels)
    plt.ylim(0.25, len(labels) + 0.75)
    plt.xticks(range(0, dmax, 10))
    plt.xticks(range(0, dmax, 5), minor=True)
    plt.xlim(0, dmax)
    plt.xlabel("microseconds")
    plt.suptitle("Micro benchmark of ClientHello production (%s)" % arch)
    plt.grid(visible=True, linewidth=0.1)
    plt.gca().set_xlim(xmin=0)
    plt.gca().set_ylim(ymin=0)
    f.subplots_adjust(hspace=0.1, left=0.26, right=0.95, bottom=0.15)
    plt.savefig("microbench-%s.svg" % arch, format="svg")

    plt.close()
