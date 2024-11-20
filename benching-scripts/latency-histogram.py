import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]


def read(fn):
    samples = []
    for line in open(fn):
        if not line:
            continue
        value = line.split()[1]
        samples.append(float(value))
    return samples


def max_bin(samples):
    return max(max(x) for x in samples)


order = ("rustls 0.23.16", "OpenSSL 3.3.2")


for out_file, title, samples in [
    (
        "tls13-resume.svg",
        "TLS1.3 server resumption",
        [
            read("rustls/latency-resume-tls13-server.tsv"),
            read("openssl-3.3.2/latency-resume-tls13-server.tsv"),
        ],
    ),
    (
        "tls12-resume.svg",
        "TLS1.2 server resumption",
        [
            read("rustls/latency-resume-tls12-server.tsv"),
            read("openssl-3.3.2/latency-resume-tls12-server.tsv"),
        ],
    ),
]:
    """
    # ensure last bin contains outliers
    bins = np.histogram_bin_edges(samples, bins=128, range=[0, max_bin(samples) * 0.75])
    bins[-1] = max_bin(samples)
    """
    bins = np.histogram_bin_edges(samples, bins=128)
    width = (bins[1] - bins[0]) * 0.5

    f, (top, bot) = plt.subplots(2, sharex=True)
    top.set_title("Latency distribution")
    top.set_ylabel("Frequency")
    top.hist(samples, bins=bins, width=width)
    bot.set_ylabel("Frequency (log)")
    bot.hist(samples, bins=bins, log=True, width=width)
    bot.set_xlabel("Latency (microseconds)")

    for p in (bot, top):
        p.set_xlim(xmin=0)
        p.grid(axis="x")
    f.subplots_adjust(hspace=0, left=0.1, right=0.95)
    f.legend(order)
    f.suptitle(title)
    f.align_ylabels()
    f.set_size_inches(10, 6)
    plt.savefig(out_file, format="svg")
