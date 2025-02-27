import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LinearLocator, FuncFormatter
from matplotlib.scale import InvertedLogTransform
import numpy as np

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
plt.rcParams["font.size"] = 8


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


order = ("rustls 0.23.16", "OpenSSL 3.0.14", "OpenSSL 3.4.0", "BoringSSL")
colours = ("dodgerblue", "firebrick", "gold", "forestgreen")


def format_micros(us):
    if us >= 1000:
        return "{:.02f}ms".format(us / 1000)
    else:
        return "{:.02f}µs".format(us)


def stats(samples, title):
    return dict(
        rowLabels="P5 P50 P90 P99".split(),
        cellText=[
            [format_micros(np.percentile(samples, 5))],
            [format_micros(np.percentile(samples, 50))],
            [format_micros(np.percentile(samples, 90))],
            [format_micros(np.percentile(samples, 99))],
        ],
    )


for out_file, title, samples in [
    (
        "latency-resume-tls13-server.svg",
        "TLS1.3 server resumption",
        [
            read("rustls/latency-resume-tls13-server.tsv"),
            read("openssl-3.0.14/latency-resume-tls13-server.tsv"),
            read("openssl-3.4.0/latency-resume-tls13-server.tsv"),
            read("boringssl/latency-resume-tls13-server.tsv"),
        ],
    ),
    (
        "latency-resume-tls12-server.svg",
        "TLS1.2 server resumption",
        [
            read("rustls/latency-resume-tls12-server.tsv"),
            read("openssl-3.0.14/latency-resume-tls12-server.tsv"),
            read("openssl-3.4.0/latency-resume-tls12-server.tsv"),
            read("boringssl/latency-resume-tls12-server.tsv"),
        ],
    ),
    (
        "latency-fullhs-tls13-server.svg",
        "TLS1.3 server full handshakes",
        [
            read("rustls/latency-fullhs-tls13-server.tsv"),
            read("openssl-3.0.14/latency-fullhs-tls13-server.tsv"),
            read("openssl-3.4.0/latency-fullhs-tls13-server.tsv"),
            read("boringssl/latency-fullhs-tls13-server.tsv"),
        ],
    ),
    (
        "latency-fullhs-tls12-server.svg",
        "TLS1.2 server full handshakes",
        [
            read("rustls/latency-fullhs-tls12-server.tsv"),
            read("openssl-3.0.14/latency-fullhs-tls12-server.tsv"),
            read("openssl-3.4.0/latency-fullhs-tls12-server.tsv"),
            read("boringssl/latency-fullhs-tls12-server.tsv"),
        ],
    ),
]:
    bins = np.histogram_bin_edges(np.log10(samples), bins=128)
    width = (bins[1] - bins[0]) * 0.9

    f, plots = plt.subplots(4, sharex=True)

    def format_y_axis(value, _):
        value = int(value)
        if value == 0:
            return "0"
        return "{:}K".format(value // 1000)

    for plot, samp, impl, colour in zip(plots, samples, order, colours):
        # linear.set_ylabel("freq")
        # linear.hist(samp, bins=bins, width=width, color=colour)
        plot.hist(np.log10(samp), bins=bins, width=width, color=colour)
        plot.set_ylabel(impl)
        plot.yaxis.set_minor_formatter(FuncFormatter(format_y_axis))
        plot.yaxis.set_major_formatter(FuncFormatter(format_y_axis))
        # log.yaxis.set_major_locator(LogLocator(subs=(1.0,), numticks=5))
        # log.yaxis.set_minor_locator(LogLocator(subs="auto", numticks=10))

    plots[-1].set_xlabel("Latency")
    plots[-1].set_xscale("log")

    def format_x_axis(x, _):
        if x > 100:
            return ""
        v = 10**x
        return format_micros(v)

    plots[-1].xaxis.set_minor_formatter(FuncFormatter(format_x_axis))
    plots[-1].xaxis.set_major_formatter(FuncFormatter(format_x_axis))

    for i in range(len(order)):
        tab = plt.table(
            bbox=[1.05, 3.1 - (1 * i), 0.15, 0.9],
            edges="open",
            **stats(samples[i], order[i]),
        )
        tab.set_fontsize(8)

    f.text(
        x=0.8,
        y=0.05,
        s="N = {}".format(len(samples[i])),
    )

    for p in plots:
        p.set_ylim(ymin=0)
        p.set_xlim(xmin=np.floor(np.min(np.log10(samples))))
        p.grid(axis="x", which="both")
    f.subplots_adjust(hspace=0, left=0.1, right=0.85)
    # f.legend(order, color=colours)
    f.suptitle(title + " latency distribution")
    f.align_ylabels()
    f.set_size_inches(9, 6)
    plt.savefig(out_file, format="svg")
