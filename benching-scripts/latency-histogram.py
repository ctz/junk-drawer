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


order = ("rustls 0.23.16", "OpenSSL 3.0.14", "OpenSSL 3.3.2", "BoringSSL")


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
    bins = np.histogram_bin_edges(samples, bins=32)
    width = (bins[1] - bins[0]) * 0.22

    f, (top, bot) = plt.subplots(2, sharex=True)
    top.set_title("Latency distribution")
    top.set_ylabel("Frequency")
    top.hist(samples, bins=bins, width=width)
    bot.set_ylabel("Frequency (log)")
    bot.hist(samples, bins=bins, log=True, width=width)
    bot.set_xlabel("Latency (microseconds)")

    for i in range(len(order)):
        f.text(
            x=0.1 + (i * 0.2), y=0.05, s=stats(samples[i], order[i]), fontsize="small"
        )

    for p in (bot, top):
        p.set_xlim(xmin=0)
        p.grid(axis="x")
    f.subplots_adjust(hspace=0, left=0.1, right=0.95, bottom=0.25)
    f.legend(order)
    f.suptitle(title)
    f.align_ylabels()
    f.set_size_inches(9, 6)
    plt.savefig(out_file, format="svg")
