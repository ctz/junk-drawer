import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LinearLocator
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


order = ("rustls 0.23.16", "OpenSSL 3.0.14", "OpenSSL 3.3.2", "BoringSSL")
colours = ("dodgerblue", "firebrick", "gold", "forestgreen")


def stats(samples, title):
    return (
        "{}:\n- min: {:g}μs\n- mean: {:g}μs\n- std dev: {:g}μs\n- max: {:g}μs".format(
            title, min(samples), np.mean(samples), np.std(samples), max(samples)
        )
    )


for out_file, title, samples in [
    (
        "latency-resume-tls13-server.svg",
        "TLS1.3 server resumption",
        [
            read("rustls/latency-resume-tls13-server.tsv"),
            read("openssl-3.0.14/latency-resume-tls13-server.tsv"),
            read("openssl-3.3.2/latency-resume-tls13-server.tsv"),
            read("boringssl/latency-resume-tls13-server.tsv"),
        ],
    ),
    (
        "latency-resume-tls12-server.svg",
        "TLS1.2 server resumption",
        [
            read("rustls/latency-resume-tls12-server.tsv"),
            read("openssl-3.0.14/latency-resume-tls12-server.tsv"),
            read("openssl-3.3.2/latency-resume-tls12-server.tsv"),
            read("boringssl/latency-resume-tls12-server.tsv"),
        ],
    ),
    (
        "latency-fullhs-tls13-server.svg",
        "TLS1.3 server full handshakes",
        [
            read("rustls/latency-fullhs-tls13-server.tsv"),
            read("openssl-3.0.14/latency-fullhs-tls13-server.tsv"),
            read("openssl-3.3.2/latency-fullhs-tls13-server.tsv"),
            read("boringssl/latency-fullhs-tls13-server.tsv"),
        ],
    ),
    (
        "latency-fullhs-tls12-server.svg",
        "TLS1.2 server full handshakes",
        [
            read("rustls/latency-fullhs-tls12-server.tsv"),
            read("openssl-3.0.14/latency-fullhs-tls12-server.tsv"),
            read("openssl-3.3.2/latency-fullhs-tls12-server.tsv"),
            read("boringssl/latency-fullhs-tls12-server.tsv"),
        ],
    ),
]:
    """
    # ensure last bin contains outliers
    bins = np.histogram_bin_edges(samples, bins=128, range=[0, max_bin(samples) * 0.75])
    bins[-1] = max_bin(samples)
    """
    bins = np.histogram_bin_edges(samples, bins=128)
    width = (bins[1] - bins[0]) * 0.9

    f, plots = plt.subplots(4, sharex=True)

    for log, samp, impl, colour in zip(plots, samples, order, colours):
        # linear.set_ylabel("freq")
        # linear.hist(samp, bins=bins, width=width, color=colour)
        log.hist(samp, bins=bins, log=True, width=width, color=colour)
        log.yaxis.set_major_locator(LogLocator(subs=(1.0,), numticks=5))
        log.yaxis.set_minor_locator(LogLocator(subs="auto", numticks=10))

    plots[1].set_ylabel("Frequency (log)")
    plots[-1].set_xlabel("Latency (microseconds)")

    for i in range(len(order)):
        f.text(
            x=0.8, y=0.75 - (0.2 * i), s=stats(samples[i], order[i]), fontsize="small"
        )

    for p in plots:
        p.set_ylim(ymin=1)
        p.set_xlim(xmin=0)
        p.grid(axis="x")
    f.subplots_adjust(hspace=0.1, left=0.1, right=0.75)
    # f.legend(order, color=colours)
    f.suptitle(title + " latency distribution")
    f.align_ylabels()
    f.set_size_inches(9, 6)
    plt.savefig(out_file, format="svg")
