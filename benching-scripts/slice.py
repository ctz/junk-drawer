import sys

_, file, *tags = sys.argv


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


print("threads\thandshake per sec per core")
for line in open(file):
    if line.strip() == "":
        continue
    parts = line.split("\t")

    if all(eq(p, t) for p, t in zip(parts, tags)):
        print(
            "%s\t%s"
            % (
                extract_which("threads", parts, "1"),
                extract_which("per-thread", parts, parts[-2]),
            )
        )
