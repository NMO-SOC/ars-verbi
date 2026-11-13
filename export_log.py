"""Export the Ask Appleyard question log (Cloudflare KV) to a spreadsheet you can open in Excel.

One-off: run `npx wrangler login` (opens a browser) once.
Usage:  python export_log.py                      -> question-log.csv
        python export_log.py --out term4.csv
        python export_log.py --namespace-id <id>  (only if the name lookup fails)

Columns: time (UTC), ip, question, model, flag, answer. `flag` marks answers where Mrs Appleyard declined or said
the guide doesn't cover it: sort by it to see what students want that the site lacks. Entries logged before
replies were saved have no answer, and entries before 13 Nov 2026 still carry a network address (new ones have none), so
the file is git-ignored: keep it off the site.
"""
import csv, json, re, subprocess, sys

TITLE = "ask-appleyard-log"
NOT_COVERED = re.compile(r"doesn.t (directly )?(cover|analyse|address)|not (covered|a question about)|I.m afraid|outside (that|this) scope|couldn.t find", re.I)

def wrangler(*args):
    p = subprocess.run(["npx", "--yes", "wrangler@latest", *args], capture_output=True, text=True, encoding="utf-8", shell=(sys.platform == "win32"))
    if p.returncode: sys.exit("wrangler failed (run `npx wrangler login` first?):\n" + (p.stderr or p.stdout)[-600:])
    return p.stdout

def json_in(text, opener):
    """wrangler may print a banner before its JSON; take from the first opener on."""
    return json.loads(text[text.index(opener):])

def find_namespace():
    for ns in json_in(wrangler("kv", "namespace", "list"), "["):
        if ns.get("title") == TITLE: return ns["id"]
    sys.exit("No KV namespace called %s; pass --namespace-id" % TITLE)

def rows(keys, get):
    """get(key) -> raw value text. Newest first."""
    out = []
    for k in sorted(keys, reverse=True):
        try: v = json_in(get(k), "{")
        except (ValueError, KeyError): continue
        a = v.get("a", "")
        out.append([k.rsplit("-", 1)[0], v.get("ip", ""), v.get("q", ""), v.get("model", ""),
                    "declined / not covered" if a and NOT_COVERED.search(a) else "", a])
    return out

def main(argv):
    ns = argv[argv.index("--namespace-id") + 1] if "--namespace-id" in argv else find_namespace()
    out = argv[argv.index("--out") + 1] if "--out" in argv else "question-log.csv"
    keys = [k["name"] for k in json_in(wrangler("kv", "key", "list", "--namespace-id", ns, "--remote"), "[")]
    print("%d log entries; reading them..." % len(keys))
    data = rows(keys, lambda k: wrangler("kv", "key", "get", k, "--namespace-id", ns, "--remote", "--text"))
    with open(out, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig so Excel shows curly quotes correctly
        w = csv.writer(f); w.writerow(["time (UTC)", "ip", "question", "model", "flag", "answer"]); w.writerows(data)
    print("Wrote %s (%d rows, %d flagged)" % (out, len(data), sum(1 for r in data if r[4])))

if __name__ == "__main__":
    main(sys.argv[1:])
