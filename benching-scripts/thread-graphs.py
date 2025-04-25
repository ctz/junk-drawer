import matplotlib.pyplot as plt
import numpy as np

import slice

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
plt.rcParams["font.size"] = 8


def read(fn, *tags):
    x = []
    y = []
    for line in slice.iter_all(fn, tags):
        x.append(int(slice.extract_which("threads", line)))
        y.append(float(slice.extract_which("per-thread", line, line[-2])))
    return x, y


openssl_3_4_file = "openssl-thread05-arm.out.txt"
openssl_3_4_version = "OpenSSL 3.4.0"
openssl_3_0_file = "openssl-host-thread02-arm.out.txt"
openssl_3_0_version = "OpenSSL 3.0.14"
rustls_file = "result-thr-23.16-2.txt"
rustls_version = "rustls 0.23.16"
rustls_fix_file = "result-thr-23.17.txt"
rustls_fix_version = "rustls 0.23.17"
boringssl_file = "boringssl-thr-02.out.txt"

plt.subplots(figsize=(9, 6), dpi=200)
lines = []

for (x, y), label in [
    (
        read(
            rustls_file,
            "handshakes",
            "?",
            "?",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "tickets",
        ),
        rustls_version + " (tickets)",
    ),
    (
        read(
            rustls_file,
            "handshakes",
            "?",
            "?",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "sessionid",
        ),
        rustls_version + " (session-id)",
    ),
    (
        read(
            openssl_3_0_file,
            "handshake-ticket",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        openssl_3_0_version + " (tickets)",
    ),
    (
        read(
            openssl_3_0_file,
            "handshake-resume",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        openssl_3_0_version + " (session-id)",
    ),
    (
        read(
            openssl_3_4_file,
            "handshake-ticket",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        openssl_3_4_version + " (tickets)",
    ),
    (
        read(
            openssl_3_4_file,
            "handshake-resume",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        openssl_3_4_version + " (session-id)",
    ),
    (
        read(
            boringssl_file,
            "handshake-ticket",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        "BoringSSL (tickets)",
    ),
    (
        read(
            boringssl_file,
            "handshake-resume",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        "BoringSSL (session-id)",
    ),
]:
    lines.append(plt.plot(x, y, marker="o", linewidth=1, markersize=1, label=label))

plt.axvline(x=80, linestyle="dotted", linewidth=0.5)
plt.ylabel("handshakes per second per thread")
plt.xlabel("Threads")
legend = plt.legend(
    loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1)
)
plt.suptitle("TLS1.2 resumed server handshake scalability vs thread count")
plt.grid(visible=True, linewidth=0.1)
plt.gca().set_xlim(xmin=0)
plt.gca().set_ylim(ymin=0)
plt.savefig("resumed-12-server.svg", format="svg")

x, y = read(
    rustls_fix_file,
    "handshakes",
    "?",
    "?",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "server",
    "server-auth",
    "tickets",
)
label = rustls_fix_version + " (tickets)"

lines[0][0].set_linestyle("dotted")
legend.get_texts()[0].set_text(label)
plt.plot(
    x,
    y,
    marker="o",
    linewidth=1,
    markersize=1,
    label=label,
    color=lines[0][0].get_color(),
)
plt.savefig("resumed-12-server-postfix.svg", format="svg")

plt.close()
plt.subplots(figsize=(9, 6), dpi=200)

lines = []

for (x, y), label in [
    (
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS13_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "tickets",
        ),
        rustls_version,
    ),
    (
        read(
            rustls_fix_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS13_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "tickets",
        ),
        rustls_fix_version,
    ),
    (
        read(
            openssl_3_0_file,
            "handshake-ticket",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        openssl_3_0_version,
    ),
    (
        read(
            openssl_3_4_file,
            "handshake-ticket",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        openssl_3_4_version,
    ),
    (
        read(
            boringssl_file,
            "handshake-ticket",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        "BoringSSL",
    ),
]:
    extra = dict()
    if label == rustls_version:
        extra = dict(linestyle="dotted")
    if label == rustls_fix_version:
        extra = dict(color=lines[0][0].get_color())

    lines.append(
        plt.plot(x, y, marker="o", linewidth=1, markersize=1, label=label, **extra)
    )


plt.axvline(x=80, linestyle="dotted", linewidth=0.5)
plt.ylabel("handshakes per second per thread")
plt.xlabel("Threads")
legend = plt.legend(
    loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1)
)
plt.suptitle("TLS1.3 resumed server handshake scalability vs thread count")
plt.grid(visible=True, linewidth=0.1)
plt.gca().set_xlim(xmin=0)
plt.gca().set_ylim(ymin=0)
plt.savefig("resumed-13-server.svg", format="svg")

lines[0][0].set_linestyle("dotted")
plt.savefig("resumed-13-server-postfix.svg", format="svg")


plt.close()
plt.subplots(figsize=(9, 6), dpi=200)

for (x, y), label in [
    (
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS13_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "no-resume",
        ),
        rustls_version,
    ),
    (
        read(
            openssl_3_0_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        openssl_3_0_version,
    ),
    (
        read(
            openssl_3_4_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        openssl_3_4_version,
    ),
    (
        read(
            boringssl_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        "BoringSSL",
    ),
]:
    plt.plot(x, y, marker="o", linewidth=1, markersize=1, label=label)


plt.axvline(x=80, linestyle="dotted", linewidth=0.5)
plt.ylabel("handshakes per second per thread")
plt.xlabel("Threads")
plt.legend(loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1))
plt.suptitle("TLS1.3 full server handshake scalability vs thread count")
plt.grid(visible=True, linewidth=0.1)
plt.gca().set_xlim(xmin=0)
plt.gca().set_ylim(ymin=0)
plt.savefig("full-server.svg", format="svg")
