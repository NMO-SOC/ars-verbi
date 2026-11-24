"""Keep Ask Appleyard's embeddings in step with the search index.

Reads public/assets/search.json and writes public/assets/embeddings.json (one 768-dim vector per chunk, same order,
int8-quantised and base64-encoded, exactly as make-embeddings.ps1 did). Only chunks whose text changed are sent to the
Worker: vectors are cached by a hash of their text in worker/embed-cache.json, so a normal edit costs a few calls.

Runs automatically from build.py and again in the Pages workflow on every push. Standard library only.
Usage: python make_embeddings.py [worker_url]
"""
import base64, hashlib, json, math, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
INDEX = os.path.join(PUBLIC, "assets", "search.json")
OUT = os.path.join(PUBLIC, "assets", "embeddings.json")
CACHE = os.path.join(ROOT, "worker", "embed-cache.json")
DEFAULT_WORKER = "https://ask-appleyard.nicholas-morlin.workers.dev/"
ORIGIN = "https://nmo-soc.github.io"   # must be in the Worker's ALLOWED_ORIGINS
DIM, BATCH = 768, 100


def chunk_text(e):
    t = "%s. %s" % (e.get("t", ""), e.get("b", ""))
    return t[:1200]


def quantise(vec):
    v = vec[:DIM]
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    q = bytes(((max(-127, min(127, int(round(x / n * 127)))) + 256) % 256) for x in v)
    return base64.b64encode(q).decode("ascii")


def embed(worker, texts):
    body = json.dumps({"embed": True, "input": texts}).encode("utf-8")
    req = urllib.request.Request(worker, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "Origin": ORIGIN,
                                          "User-Agent": "ars-verbi-embeddings/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))["data"]
            if len(data) != len(texts):
                raise ValueError("Worker returned %d vectors for %d texts" % (len(data), len(texts)))
            return [d["embedding"] for d in data]
        except Exception as e:
            if attempt == 2:
                raise
            print("  embed retry after error: %s" % e)
            time.sleep(3 * (attempt + 1))


def run(worker=DEFAULT_WORKER):
    """Bring embeddings.json up to date. Returns True if it is in step with search.json afterwards."""
    idx = json.load(open(INDEX, encoding="utf-8"))
    texts = [chunk_text(e) for e in idx]
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
    try:
        cache = json.load(open(CACHE, encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    missing = sorted({k for k in keys if k not in cache})
    todo = [(k, texts[keys.index(k)]) for k in missing]
    if todo:
        print("embeddings: %d of %d chunks changed, sending to the Worker" % (len(todo), len(texts)))
        try:
            for i in range(0, len(todo), BATCH):
                part = todo[i:i + BATCH]
                for (k, _), vec in zip(part, embed(worker, [t for _, t in part])):
                    cache[k] = quantise(vec)
        except Exception as e:
            print("embeddings: Worker unavailable (%s); keeping the previous embeddings" % e)
            return False
    out = {"dim": DIM, "v": [cache[k] for k in keys]}
    old = None
    try:
        old = json.load(open(OUT, encoding="utf-8-sig"))
    except (OSError, ValueError):
        pass
    if old != out:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
    # keep only vectors still in use, so the cache doesn't grow forever
    live = set(keys)
    cache = {k: v for k, v in cache.items() if k in live}
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, separators=(",", ":"), sort_keys=True)
    print("embeddings: %d vectors, %s" % (len(keys), "updated" if old != out else "already up to date"))
    return True


def refresh_version_strings():
    """Pages request embeddings.json?v=<content hash>; point them at the current file so browsers don't use a stale copy."""
    ver = hashlib.md5(open(OUT, "rb").read()).hexdigest()[:8]
    n = 0
    for fn in os.listdir(PUBLIC):
        if fn.endswith(".html"):
            p = os.path.join(PUBLIC, fn)
            s = open(p, encoding="utf-8").read()
            s2 = re.sub(r"embeddings\.json\?v=[0-9a-f]+", "embeddings.json?v=" + ver, s)
            if s2 != s:
                open(p, "w", encoding="utf-8").write(s2); n += 1
    return n


if __name__ == "__main__":
    ok = run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORKER)
    if ok:
        refresh_version_strings()
    sys.exit(0 if ok else 1)
