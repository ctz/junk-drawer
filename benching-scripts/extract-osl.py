import sys

lines = open(sys.argv[-1], "r").readlines()


def out(line):
    items = line.split()
    for i in items:
        if i[0].isdigit():
            print(i)
            return


def extract(introducer, first, second):
    inside = False
    done_first = False
    done_second = False
    for l in lines:
        if introducer in l:
            inside = True
            continue
        if inside and not done_first and l.startswith(first):
            out(l)
            done_first = True
        if inside and not done_second and l.startswith(second):
            out(l)
            done_second = True


print("bulk column ----")
extract("bulk ECDHE-RSA-AES128-GCM-SHA256", "send", "recv")
extract("bulk TLS_AES_256_GCM_SHA384", "send", "recv")

print("handshakes column ----")
client, server = "handshakes\tclient", "handshakes\tserver"
extract("handshake ECDHE-RSA-AES256-GCM-SHA384", client, server)
extract("handshake ECDHE-ECDSA-AES256-GCM-SHA384", client, server)
extract("handshake TLS_AES_256_GCM_SHA384", client, server)
extract("--ecdsa handshake TLS_AES_256_GCM_SHA384", client, server)

print("resumption column ----")
extract("handshake-resume ECDHE-RSA-AES256-GCM-SHA384", client, server)
extract("handshake-ticket TLS_AES_256_GCM_SHA384", client, server)
