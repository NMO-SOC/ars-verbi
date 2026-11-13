"""Export the Ask Appleyard question log (Cloudflare KV) to a spreadsheet you can open in Excel.

One-off: run `npx wrangler login` (opens a browser) once.
Usage:  python export_log.py                      -> question-log.csv
        python export_log.py --out term4.csv
        python export_log.py --namespace-id <id>  (only if the name lookup fails)

Columns: concern, why, time (UTC), ip, question, model, flag, answer.
- `concern` is for wellbeing and safeguarding. The sheet lists every HIGH entry first, then "check" entries, then
  the rest newest first, and the terminal prints them too. HIGH is a student describing harm to themselves or
  someone else, or being unsafe; "check" is weaker (hopeless, bullied, anxious...), or the bot itself pointed the
  student to Kids Helpline, or the entry could not be read. It is a keyword net, not a judgement: read the question,
  and expect some false alarms (a question about a text can use these words) and some misses. It does not replace
  reading the log.
- `flag` marks answers where Mrs Appleyard declined or said the guide doesn't cover it: sort by it to see what
  students want that the site lacks.
Entries logged before replies were saved have no answer. The file holds network addresses, so it is git-ignored:
keep it off the site.
"""
import csv, json, re, subprocess, sys

TITLE = "ask-appleyard-log"
NOT_COVERED = re.compile(r"doesn.t (directly )?(cover|analyse|address)|not (covered|a question about)|I.m afraid|outside (that|this) scope|couldn.t find", re.I)
# first person or direct statements only, so literary questions ("why does Miranda hit...") don't flood the list
HIGH = re.compile(r"\bsuicid\w*|\bkill(ing)? (my|him|her|them)sel(f|ves)\b|\bend (my life|it all)\b|\bwant(s|ed)? to die\b|"
                  r"\bdon.?t want to (be here|live|exist)\b|\bself.?harm\w*|\b(hurt|hurting|cut|cutting|harm|harming) (my|him|her|them)sel(f|ves)\b|"
                  r"\boverdos\w*|\b(abus\w*|hit|hits|hitting|hurt|hurts|beat|beats|touch\w*|rap(e|es|ed)|molest\w*|assault\w*) (me|my)\b|"
                  r"\bsexual(ly)? (assault|abus)\w*|\bunsafe (at home|with)\b|\b(being|am|was|been) (abused|molested|raped|assaulted)\b|"
                  r"\brun(ning)? away from home\b", re.I)
CHECK = re.compile(r"\bhopeless\b|\bworthless\b|\bno point\b|\bcan.?t (cope|go on|do this anymore|take it)\b|\bdepress\w*|\bpanic attack\w*|"
                   r"\banxiety attack\w*|\banxious\b|\beating disorder\b|\bbull(y|ied|ies|ying)\b|\bharass\w*|\bhate myself\b|\blonely\b|"
                   r"\bscared of\b|\bafraid of (him|her|them|my)\b|\babus(e|ed|ing)\b|\bgive up\b", re.I)
BOT_HELP = re.compile(r"Kids Helpline|1800 55 1800|wellbeing team", re.I)

def concern(q, a):
    """(level, why): level is 'HIGH', 'check' or ''. why lists the matched words."""
    hi = sorted({m.group(0).lower() for m in HIGH.finditer(q)})
    if hi: return "HIGH", ", ".join(hi)
    lo = sorted({m.group(0).lower() for m in CHECK.finditer(q)})
    if BOT_HELP.search(a or ""): lo.append("Mrs Appleyard pointed to Kids Helpline / wellbeing")
    return ("check", ", ".join(lo)) if lo else ("", "")

def wrangler(*args):
    p = subprocess.run(["npx", "--yes", "wrangler@latest", *args], capture_output=True, text=True, encoding="utf-8", shell=(sys.platform == "win32"))
    if p.returncode: raise RuntimeError("wrangler failed (run `npx wrangler login` first?):\n" + (p.stderr or p.stdout)[-600:])
    return p.stdout

def json_in(text, opener):
    """wrangler may print a banner before its JSON; take from the first opener on."""
    return json.loads(text[text.index(opener):])

def find_namespace():
    for ns in json_in(wrangler("kv", "namespace", "list"), "["):
        if ns.get("title") == TITLE: return ns["id"]
    sys.exit("No KV namespace called %s; pass --namespace-id" % TITLE)

def read_with_retry(get, k, tries=3):
    """Cloudflare occasionally fails a single read: try again before giving up."""
    for attempt in range(tries):
        try: return get(k)
        except RuntimeError:
            if attempt == tries - 1: raise

def rows(keys, get):
    """get(key) -> raw value text. HIGH concerns first, then 'check', then the rest; newest first within each."""
    out = []
    for k in sorted(keys, reverse=True):
        try: v = json_in(read_with_retry(get, k), "{")
        except (RuntimeError, ValueError, KeyError):   # never skip an entry silently: show it, so it can be read in Cloudflare
            out.append(["check", "this entry could not be read: open it in the Cloudflare dashboard", k.rsplit("-", 1)[0], "",
                        "(unreadable log entry %s)" % k, "", "", ""])
            continue
        q, a = v.get("q", ""), v.get("a", "")
        level, why = concern(q, a)
        out.append([level, why, k.rsplit("-", 1)[0], v.get("ip", ""), q, v.get("model", ""),
                    "declined / not covered" if a and NOT_COVERED.search(a) else "", a])
    rank = {"HIGH": 0, "check": 1, "": 2}
    return sorted(out, key=lambda r: rank[r[0]])   # stable: keeps newest-first inside each group

def main(argv):
    ns = argv[argv.index("--namespace-id") + 1] if "--namespace-id" in argv else find_namespace()
    out = argv[argv.index("--out") + 1] if "--out" in argv else "question-log.csv"
    keys = [k["name"] for k in json_in(wrangler("kv", "key", "list", "--namespace-id", ns, "--remote"), "[")]
    print("%d log entries; reading them..." % len(keys))
    data = rows(keys, lambda k: wrangler("kv", "key", "get", k, "--namespace-id", ns, "--remote", "--text"))
    with open(out, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig so Excel shows curly quotes correctly
        w = csv.writer(f); w.writerow(["concern", "why", "time (UTC)", "ip", "question", "model", "flag", "answer"]); w.writerows(data)
    hi, chk = [r for r in data if r[0] == "HIGH"], [r for r in data if r[0] == "check"]
    print("Wrote %s (%d rows; %d HIGH concern, %d to check, %d declined/not covered)" % (out, len(data), len(hi), len(chk), sum(1 for r in data if r[6])))
    for label, group in (("HIGH CONCERN", hi), ("CHECK", chk)):
        for r in group: print("  %s  %s  [%s]  %s" % (label, r[2][:19], r[1], r[4][:160]))

if __name__ == "__main__":
    try: main(sys.argv[1:])
    except RuntimeError as e: sys.exit(str(e))
