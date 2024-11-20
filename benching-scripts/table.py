import sys

_, file, *colspec = sys.argv


def extract_which(name, parts, default=None):
    try:
        idx = parts.index(name)
        assert idx is not None
        return parts[idx + 1]
    except:
        return default


def eq(v, p):
    if p == v:
        return True
    if p == "?":
        return True


columns = []

for col in colspec:
    head, tags = col.split("=")
    tags = tags.split()
    columns.append([head, tags, []])

for line in open(file):
    if line.strip() == "":
        continue
    parts = line.split("\t")

    for head, tags, out in columns:
        if all(eq(p, t) for p, t in zip(parts, tags)):
            threads = extract_which("threads", parts, "1")
            measure = extract_which("per-thread", parts, parts[-2])
            out.append(threads)
            out.append(measure)

print("threads\t" + ("\t".join(col[0] for col in columns)))
for threads in columns[0][2][::2]:
    print(
        threads
        + "\t"
        + "\t".join(extract_which(threads, col[2], "0") for col in columns)
    )
