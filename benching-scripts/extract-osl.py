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
    found_first = None
    found_second = None
    for l in lines:
        if introducer in l:
            inside = True
            continue
        if inside and not found_first and l.startswith(first):
            found_first = l
        if inside and not found_second and l.startswith(second):
            found_second = l

        if found_first and found_second:
            out(found_first)
            out(found_second)
            return


print("bulk column ----")
extract("bulk ECDHE-RSA-AES128-GCM-SHA256", "bulk\tsend", "bulk\trecv")
extract("bulk TLS_AES_256_GCM_SHA384", "bulk\tsend", "bulk\trecv")

print("handshakes column ----")
client, server = "handshakes\tclient", "handshakes\tserver"
extract("handshake ECDHE-RSA-AES256-GCM-SHA384", client, server)
extract("handshake ECDHE-ECDSA-AES256-GCM-SHA384", client, server)
extract("handshake TLS_AES_256_GCM_SHA384", client, server)
extract("--ecdsa handshake TLS_AES_256_GCM_SHA384", client, server)

print("resumption column ----")
client, server = "handshake-resume\tclient", "handshake-resume\tserver"
extract("handshake-resume ECDHE-RSA-AES256-GCM-SHA384", client, server)
client, server = "handshake-ticket\tclient", "handshake-ticket\tserver"
extract("handshake-ticket TLS_AES_256_GCM_SHA384", client, server)
