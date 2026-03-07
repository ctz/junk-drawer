import matplotlib.pyplot as plt
import numpy as np

import slice

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
plt.rcParams["font.size"] = 8


def read(fn, *tags, **kwargs):
    for line in slice.iter_all(fn, tags, **kwargs):
        return float(line[-2])
    raise ValueError(f"Couldn't find {tags} for {fn}")


openssl_file = "march-7-osl-3.6.1.txt"
openssl_version = "OpenSSL 3.6.1"
rustls_file = "march-7-0.23.37.txt"
rustls_version = "rustls 0.23.37"
boringssl_file = "march-7-boring.txt"
boringssl_version = "BoringSSL 30cd935"


impls = [
    boringssl_version,
    openssl_version,
    rustls_version,
]

groups = [
    (
        "transfer, 1.2, aes-128-gcm, sending",
        read(
            boringssl_file,
            "bulk",
            "send",
            "?",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ),
        read(
            openssl_file,
            "bulk",
            "send",
            "?",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ),
        read(
            rustls_file,
            "bulk",
            "?",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "?",
            "send",
        ),
    ),
    (
        "transfer, 1.2, aes-128-gcm, receiving",
        read(
            boringssl_file,
            "bulk",
            "recv",
            "?",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ),
        read(
            openssl_file,
            "bulk",
            "recv",
            "?",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ),
        read(
            rustls_file,
            "bulk",
            "?",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "?",
            "recv",
        ),
    ),
    (
        "transfer, 1.3, aes-256-gcm, sending",
        read(
            boringssl_file,
            "bulk",
            "send",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "bulk",
            "send",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            rustls_file,
            "bulk",
            "?",
            "TLS13_AES_256_GCM_SHA384",
            "?",
            "send",
        ),
    ),
    (
        "transfer, 1.3, aes-256-gcm, receiving",
        read(
            boringssl_file,
            "bulk",
            "recv",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "bulk",
            "recv",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            rustls_file,
            "bulk",
            "?",
            "TLS13_AES_256_GCM_SHA384",
            "?",
            "recv",
        ),
    ),
]

fig, ax = plt.subplots(figsize=(9, 6), dpi=200)

for i, impl in enumerate(impls):
    width = 0.2
    gap = 0.03

    rects = plt.barh(
        [g + (width + gap) * i for g in range(len(groups))],
        [g[i + 1] for g in groups],
        width,
        label=impl,
    )
    plt.bar_label(rects, labels=["%d" % (g[i + 1]) for g in groups], padding=3)


plt.xlabel("megabytes per second (single core)")
legend = plt.legend(
    loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1)
)
plt.suptitle("Bulk throughput speed comparison (megabytes per second)")
plt.grid(visible=True, linewidth=0.1, axis="x")
plt.gca().set_xlim(xmin=0)
ax.invert_yaxis()
ax.set_yticks([x + width for x in range(len(groups))], labels=[x[0] for x in groups])
fig.subplots_adjust(hspace=0.1, left=0.23, right=0.95, bottom=0.1)

plt.savefig("2026-03-07-transfer.svg", format="svg")
plt.close()

groups = [
    (
        "full handshakes, 1.2, rsa, client",
        read(
            boringssl_file,
            "handshakes",
            "client",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "client",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "no-resume",
        ),
    ),
    (
        "full handshakes, 1.2, rsa, server",
        read(
            boringssl_file,
            "handshakes",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "no-resume",
        ),
    ),
    (
        "full handshakes, 1.2, ecdsa, client",
        read(
            boringssl_file,
            "handshakes",
            "client",
            "?",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "client",
            "?",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "EcdsaP256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "no-resume",
        ),
    ),
    (
        "full handshakes, 1.2, ecdsa, server",
        read(
            boringssl_file,
            "handshakes",
            "server",
            "?",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "server",
            "?",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "EcdsaP256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "no-resume",
        ),
    ),
    # ---
    (
        "full handshakes, 1.3, rsa, client",
        read(
            boringssl_file,
            "handshakes",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS13_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "no-resume",
        ),
    ),
    (
        "full handshakes, 1.3, rsa, server",
        read(
            boringssl_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
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
    ),
    (
        "full handshakes, 1.3, ecdsa, client",
        read(
            boringssl_file,
            "handshakes",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
            filter="--ecdsa",
        ),
        read(
            openssl_file,
            "handshakes",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
            filter="--ecdsa",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "EcdsaP256",
            "TLS13_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "no-resume",
        ),
    ),
    (
        "full handshakes, 1.3, ecdsa, server",
        read(
            boringssl_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
            filter="--ecdsa",
        ),
        read(
            openssl_file,
            "handshakes",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
            filter="--ecdsa",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "EcdsaP256",
            "TLS13_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "no-resume",
        ),
    ),
]

fig, ax = plt.subplots(figsize=(9, 6), dpi=200)

for i, impl in enumerate(impls):
    width = 0.2
    gap = 0.03

    rects = plt.barh(
        [g + (width + gap) * i for g in range(len(groups))],
        [g[i + 1] for g in groups],
        width,
        label=impl,
    )
    plt.bar_label(rects, labels=["%d" % (g[i + 1]) for g in groups], padding=3)


plt.xlabel("full handshakes per second (single core)")
legend = plt.legend(
    loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1)
)
plt.suptitle("Full handshake speed comparison (handshakes per second)")
plt.grid(visible=True, linewidth=0.1, axis="x")
plt.gca().set_xlim(xmin=0)
ax.invert_yaxis()
ax.set_yticks([x + width for x in range(len(groups))], labels=[x[0] for x in groups])
fig.subplots_adjust(hspace=0.1, left=0.23, right=0.95, bottom=0.1)

plt.savefig("2026-03-07-full-handshake.svg", format="svg")
plt.close()

groups = [
    (
        "resumed handshakes, 1.2, client",
        read(
            boringssl_file,
            "handshake-resume",
            "client",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshake-resume",
            "client",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "sessionid",
        ),
    ),
    (
        "resumed handshakes, 1.2, server",
        read(
            boringssl_file,
            "handshake-resume",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            openssl_file,
            "handshake-resume",
            "server",
            "?",
            "ECDHE-RSA-AES256-GCM-SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "server",
            "server-auth",
            "sessionid",
        ),
    ),
    # ---
    (
        "resumed handshakes, 1.3, client",
        read(
            boringssl_file,
            "handshake-ticket",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "handshake-ticket",
            "client",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            rustls_file,
            "handshakes",
            "?",
            "Rsa2048",
            "TLS13_AES_256_GCM_SHA384",
            "client",
            "server-auth",
            "tickets",
        ),
    ),
    (
        "resumed handshakes, 1.3, server",
        read(
            boringssl_file,
            "handshake-ticket",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
        read(
            openssl_file,
            "handshake-ticket",
            "server",
            "?",
            "TLS_AES_256_GCM_SHA384",
        ),
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
    ),
]

fig, ax = plt.subplots(figsize=(9, 6), dpi=200)

for i, impl in enumerate(impls):
    width = 0.2
    gap = 0.03

    rects = plt.barh(
        [g + (width + gap) * i for g in range(len(groups))],
        [g[i + 1] for g in groups],
        width,
        label=impl,
    )
    plt.bar_label(rects, labels=["%d" % (g[i + 1]) for g in groups], padding=3)


plt.xlabel("resumed handshakes per second (single core)")
legend = plt.legend(
    loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, 1.1)
)
plt.suptitle("Resumed handshake speed comparison (handshakes per second)")
plt.grid(visible=True, linewidth=0.1, axis="x")
plt.gca().set_xlim(xmin=0)
ax.invert_yaxis()
ax.set_yticks([x + width for x in range(len(groups))], labels=[x[0] for x in groups])
fig.subplots_adjust(hspace=0.1, left=0.23, right=0.95, bottom=0.1)

plt.savefig("2026-03-07-resumed-handshake.svg", format="svg")
plt.close()
